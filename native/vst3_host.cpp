// Minimal Linux VST3 effect host. Native code runs only in a disposable helper
// process.
#define INIT_CLASS_IID
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/gui/iplugview.h"
#include "pluginterfaces/gui/iplugviewcontentscalesupport.h"
#include "pluginterfaces/vst/ivstaudioprocessor.h"
#include "pluginterfaces/vst/ivsteditcontroller.h"
#include "pluginterfaces/vst/ivsthostapplication.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
#include "pluginterfaces/vst/ivstprocesscontext.h"
#include <algorithm>
#include <atomic>
#include <cmath>
#include <chrono>
#include <functional>
#include <iomanip>
#include <cstring>
#include <dlfcn.h>
#include <map>
#include <memory>
#include <stdexcept>
#include <string>
#include <sstream>
#include <vector>
#include <poll.h>
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace {
thread_local std::string error;
constexpr size_t maxState = 1024 * 1024;
bool equal(const TUID id, const FUID &expected) {
  TUID bytes;
  expected.toTUID(bytes);
  return std::memcmp(id, bytes, 16) == 0;
}
std::string quote(const std::string &s) {
  std::string out = "\"";
  for (unsigned char c : s) {
    if (c == '"' || c == '\\') {
      out += '\\';
      out += c;
    } else if (c >= 32)
      out += c;
  }
  return out + '"';
}
std::string decimal(double value) {
  std::ostringstream stream; stream << std::setprecision(17) << value; return stream.str();
}
std::string utf8(const TChar *s) {
  std::string out;
  for (int i = 0; i < 128 && s[i]; ++i) {
    uint32_t c = s[i];
    if (c >= 0xd800 && c <= 0xdbff && i + 1 < 128 && s[i + 1] >= 0xdc00 &&
        s[i + 1] <= 0xdfff)
      c = 0x10000 + ((c - 0xd800) << 10) + (s[++i] - 0xdc00);
    if (c < 128)
      out += char(c);
    else if (c < 2048) {
      out += char(0xc0 | (c >> 6));
      out += char(0x80 | (c & 63));
    } else if (c < 65536) {
      out += char(0xe0 | (c >> 12));
      out += char(0x80 | ((c >> 6) & 63));
      out += char(0x80 | (c & 63));
    } else {
      out += char(0xf0 | (c >> 18));
      out += char(0x80 | ((c >> 12) & 63));
      out += char(0x80 | ((c >> 6) & 63));
      out += char(0x80 | (c & 63));
    }
  }
  return out;
}
#define REFCOUNT                                                               \
  uint32 PLUGIN_API addRef() override { return ++refs; }                       \
  uint32 PLUGIN_API release() override {                                       \
    auto n = --refs;                                                           \
    if (!n)                                                                    \
      delete this;                                                             \
    return n;                                                                  \
  }                                                                            \
  std::atomic<uint32> refs{1};
class Attributes final : public IAttributeList {
  struct Value {
    int64 i{};
    double f{};
    std::u16string s;
    std::vector<char> b;
  };
  std::map<std::string, Value> values;

public:
  REFCOUNT
  tresult PLUGIN_API queryInterface(const TUID id, void **obj) override {
    if (equal(id, IAttributeList::iid) || equal(id, FUnknown::iid)) {
      *obj = this;
      addRef();
      return kResultOk;
    }
    *obj = nullptr;
    return kNoInterface;
  }
  tresult PLUGIN_API setInt(AttrID id, int64 v) override {
    values[id].i = v;
    return kResultOk;
  }
  tresult PLUGIN_API getInt(AttrID id, int64 &v) override {
    if (!values.count(id))
      return kResultFalse;
    v = values[id].i;
    return kResultOk;
  }
  tresult PLUGIN_API setFloat(AttrID id, double v) override {
    values[id].f = v;
    return kResultOk;
  }
  tresult PLUGIN_API getFloat(AttrID id, double &v) override {
    if (!values.count(id))
      return kResultFalse;
    v = values[id].f;
    return kResultOk;
  }
  tresult PLUGIN_API setString(AttrID id, const TChar *v) override {
    values[id].s = std::u16string(reinterpret_cast<const char16_t *>(v));
    return kResultOk;
  }
  tresult PLUGIN_API getString(AttrID id, TChar *v, uint32 bytes) override {
    if (!values.count(id) || bytes < 2)
      return kResultFalse;
    auto &s = values[id].s;
    size_t n = std::min<size_t>(s.size(), bytes / 2 - 1);
    std::memcpy(v, s.data(), n * 2);
    v[n] = 0;
    return kResultOk;
  }
  tresult PLUGIN_API setBinary(AttrID id, const void *v,
                               uint32 bytes) override {
    if (bytes > maxState)
      return kOutOfMemory;
    values[id].b.assign((const char *)v, (const char *)v + bytes);
    return kResultOk;
  }
  tresult PLUGIN_API getBinary(AttrID id, const void *&v,
                               uint32 &bytes) override {
    if (!values.count(id))
      return kResultFalse;
    v = values[id].b.data();
    bytes = values[id].b.size();
    return kResultOk;
  }
};
class Message final : public IMessage {
  std::string name;
  Attributes *attrs = new Attributes;

public:
  ~Message() { attrs->release(); }
  REFCOUNT
  tresult PLUGIN_API queryInterface(const TUID id, void **obj) override {
    if (equal(id, IMessage::iid) || equal(id, FUnknown::iid)) {
      *obj = this;
      addRef();
      return kResultOk;
    }
    *obj = nullptr;
    return kNoInterface;
  }
  FIDString PLUGIN_API getMessageID() override { return name.c_str(); }
  void PLUGIN_API setMessageID(FIDString id) override { name = id ? id : ""; }
  IAttributeList *PLUGIN_API getAttributes() override { return attrs; }
};
#include "vst3_editor.h"
class Host final : public IHostApplication, public IComponentHandler {
public:
  std::atomic<uint32> refs{1};
  EditorFrame* run_loop = nullptr;
  std::function<void(ParamID, ParamValue)> edit;
  int32 restartFlags = 0;
  uint32 PLUGIN_API addRef() override { return ++refs; }
  uint32 PLUGIN_API release() override { return --refs; }
  tresult PLUGIN_API queryInterface(const TUID id, void **obj) override {
    if (equal(id, IHostApplication::iid) || equal(id, FUnknown::iid))
      *obj = static_cast<IHostApplication *>(this);
    else if (equal(id, IComponentHandler::iid))
      *obj = static_cast<IComponentHandler *>(this);
    else if (equal(id, Linux::IRunLoop::iid) && run_loop)
      return run_loop->queryInterface(id, obj);
    else {
      *obj = nullptr;
      return kNoInterface;
    }
    addRef();
    return kResultOk;
  }
  tresult PLUGIN_API getName(String128 name) override {
    const char *text = "SoundSausage";
    int i = 0;
    for (; text[i]; i++)
      name[i] = text[i];
    name[i] = 0;
    return kResultOk;
  }
  tresult PLUGIN_API createInstance(TUID cid, TUID id, void **obj) override {
    *obj = nullptr;
    if (equal(cid, IMessage::iid) && equal(id, IMessage::iid)) {
      *obj = new Message;
      return kResultOk;
    }
    if (equal(cid, IAttributeList::iid) && equal(id, IAttributeList::iid)) {
      *obj = new Attributes;
      return kResultOk;
    }
    return kNoInterface;
  }
  tresult PLUGIN_API beginEdit(ParamID) override { return kResultOk; }
  tresult PLUGIN_API performEdit(ParamID id, ParamValue value) override {
    if (!std::isfinite(value) || value < 0 || value > 1) return kInvalidArgument;
    if (edit) edit(id, value);
    return kResultOk;
  }
  tresult PLUGIN_API endEdit(ParamID) override { return kResultOk; }
  tresult PLUGIN_API restartComponent(int32 flags) override {
    restartFlags |= flags;
    return kResultOk;
  }
};
class Stream final : public IBStream {
public:
  std::vector<char> bytes;
  int64 pos = 0;
  bool failed = false;
  uint32 PLUGIN_API addRef() override { return 1; }
  uint32 PLUGIN_API release() override { return 1; }
  tresult PLUGIN_API queryInterface(const TUID id, void **obj) override {
    if (equal(id, IBStream::iid) || equal(id, FUnknown::iid)) {
      *obj = this;
      return kResultOk;
    }
    *obj = nullptr;
    return kNoInterface;
  }
  tresult PLUGIN_API read(void *buffer, int32 n, int32 *got) override {
    if (n < 0)
      return kInvalidArgument;
    int32 count = std::min<int64>(n, bytes.size() - pos);
    if (count > 0)
      std::memcpy(buffer, bytes.data() + pos, count);
    pos += count;
    if (got)
      *got = count;
    return count == n ? kResultOk : kResultFalse;
  }
  tresult PLUGIN_API write(void *buffer, int32 n, int32 *written) override {
    if (n < 0 || pos + n > int64(maxState)) {
      failed = true;
      return kOutOfMemory;
    }
    if (pos + n > int64(bytes.size()))
      bytes.resize(pos + n);
    std::memcpy(bytes.data() + pos, buffer, n);
    pos += n;
    if (written)
      *written = n;
    return kResultOk;
  }
  tresult PLUGIN_API seek(int64 offset, int32 mode, int64 *result) override {
    int64 p = offset + (mode == kIBSeekCur   ? pos
                        : mode == kIBSeekEnd ? bytes.size()
                                             : 0);
    if (p < 0 || p > int64(bytes.size()))
      return kInvalidArgument;
    pos = p;
    if (result)
      *result = p;
    return kResultOk;
  }
  tresult PLUGIN_API tell(int64 *result) override {
    if (!result)
      return kInvalidArgument;
    *result = pos;
    return kResultOk;
  }
};
class Queue final : public IParamValueQueue {
public:
  ParamID id;
  double value;
  bool present = false;
  Queue(ParamID id, double value) : id(id), value(value), present(true) {}
  uint32 PLUGIN_API addRef() override { return 1; }
  uint32 PLUGIN_API release() override { return 1; }
  tresult PLUGIN_API queryInterface(const TUID uid, void **obj) override {
    if (equal(uid, IParamValueQueue::iid) || equal(uid, FUnknown::iid)) {
      *obj = this;
      return kResultOk;
    }
    *obj = nullptr;
    return kNoInterface;
  }
  ParamID PLUGIN_API getParameterId() override { return id; }
  int32 PLUGIN_API getPointCount() override { return present ? 1 : 0; }
  tresult PLUGIN_API getPoint(int32 index, int32 &offset,
                              ParamValue &v) override {
    if (index || !present)
      return kResultFalse;
    offset = 0;
    v = value;
    return kResultOk;
  }
  tresult PLUGIN_API addPoint(int32, ParamValue v, int32 &index) override {
    value = v;
    present = true;
    index = 0;
    return kResultOk;
  }
};
class Changes final : public IParameterChanges {
public:
  std::vector<std::unique_ptr<Queue>> values;
  uint32 PLUGIN_API addRef() override { return 1; }
  uint32 PLUGIN_API release() override { return 1; }
  tresult PLUGIN_API queryInterface(const TUID uid, void **obj) override {
    if (equal(uid, IParameterChanges::iid) || equal(uid, FUnknown::iid)) {
      *obj = this;
      return kResultOk;
    }
    *obj = nullptr;
    return kNoInterface;
  }
  int32 PLUGIN_API getParameterCount() override { return values.size(); }
  IParamValueQueue *PLUGIN_API getParameterData(int32 i) override {
    return i >= 0 && i < int(values.size()) ? values[i].get() : nullptr;
  }
  IParamValueQueue *PLUGIN_API addParameterData(const ParamID &id,
                                                int32 &index) override {
    for (size_t i = 0; i < values.size(); i++)
      if (values[i]->id == id) {
        index = i;
        return values[i].get();
      }
    if (values.size() >= 4096)
      return nullptr;
    values.push_back(std::make_unique<Queue>(id, 0));
    index = values.size() - 1;
    return values.back().get();
  }
};
struct Module {
  void *lib = nullptr;
  IPluginFactory *factory = nullptr;
  bool entered = false;
  using Entry = bool (*)(void *);
  using Exit = bool (*)();
  explicit Module(const char *path) {
    lib = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    if (!lib)
      throw std::runtime_error(dlerror());
    try {
      if (auto enter = (Entry)dlsym(lib, "ModuleEntry")) {
        if (!enter(lib))
          throw std::runtime_error("VST3 ModuleEntry failed.");
        entered = true;
      }
      auto get = (IPluginFactory * (*)()) dlsym(lib, "GetPluginFactory");
      if (!get)
        throw std::runtime_error("No VST3 plug-in factory.");
      factory = get();
      if (!factory)
        throw std::runtime_error("No VST3 factory instance.");
    } catch (...) {
      if (entered)
        if (auto leave = (Exit)dlsym(lib, "ModuleExit"))
          leave();
      dlclose(lib);
      lib = nullptr;
      throw;
    }
  }
  ~Module() {
    if (factory)
      factory->release();
    if (lib) {
      if (entered)
        if (auto leave = (Exit)dlsym(lib, "ModuleExit"))
          leave();
      dlclose(lib);
    }
  }
};
struct Instance {
  std::unique_ptr<Module> module;
  EditorFrame editor;
  Host host;
  IPlugView* view = nullptr;
  bool attached = false;
  IComponent *component = nullptr;
  IAudioProcessor *processor = nullptr;
  IEditController *controller = nullptr;
  IConnectionPoint *from = nullptr, *to = nullptr;
  bool initialized = false, controllerInit = false, active = false,
       processing = false;
  int block = 1024;
  double rate;
  int64 position = 0;
  Changes pending;
  std::vector<float> left, right, outLeft, outRight;
  Instance(const char *path, const char *classId, double rate)
      : module(new Module(path)), rate(rate) {
    host.run_loop = &editor;
    IPluginFactory3* factory3 = nullptr;
    if (module->factory->queryInterface(IPluginFactory3::iid, (void**)&factory3) == kResultOk && factory3) {
      factory3->setHostContext(static_cast<IHostApplication*>(&host)); factory3->release();
    }
    FUID cid;
    if (!cid.fromString(classId))
      throw std::runtime_error("Invalid VST3 class identifier.");
    if (module->factory->createInstance(cid, IComponent::iid,
                                        (void **)&component) != kResultOk ||
        !component)
      throw std::runtime_error("Cannot create VST3 component.");
  }
  void setup() {
    host.edit = [this](ParamID id, ParamValue value) {
      int32 index; auto* queue = pending.addParameterData(id, index);
      if (queue) queue->addPoint(0, value, index);
    };
    if (component->initialize(static_cast<IHostApplication *>(&host)) !=
        kResultOk)
      throw std::runtime_error("VST3 initialization failed.");
    initialized = true;
    if (component->queryInterface(IAudioProcessor::iid, (void **)&processor) !=
            kResultOk ||
        !processor)
      throw std::runtime_error("VST3 has no audio processor.");
    if (component->queryInterface(IEditController::iid, (void **)&controller) !=
        kResultOk) {
      TUID id;
      if (component->getControllerClassId(id) == kResultOk &&
          module->factory->createInstance(id, IEditController::iid,
                                          (void **)&controller) == kResultOk &&
          controller) {
        if (controller->initialize(static_cast<IHostApplication *>(&host)) !=
            kResultOk)
          throw std::runtime_error("VST3 controller initialization failed.");
        controllerInit = true;
      }
    }
    if (controller) {
      controller->setComponentHandler(&host);
      component->queryInterface(IConnectionPoint::iid, (void **)&from);
      controller->queryInterface(IConnectionPoint::iid, (void **)&to);
      if (from && to) {
        from->connect(to);
        to->connect(from);
      }
      Stream state;
      if (component->getState(&state) == kResultOk) {
        state.pos = 0;
        controller->setComponentState(&state);
      }
    }
    if (component->getBusCount(kAudio, kInput) != 1 ||
        component->getBusCount(kAudio, kOutput) != 1)
      throw std::runtime_error(
          "Choose a VST3 effect with one stereo input and output bus.");
    SpeakerArrangement stereo = SpeakerArr::kStereo;
    if (processor->setBusArrangements(&stereo, 1, &stereo, 1) != kResultTrue)
      throw std::runtime_error("This VST3 effect does not accept stereo.");
    for (auto dir : {kInput, kOutput}) {
      BusInfo info{};
      if (component->getBusInfo(kAudio, dir, 0, info) != kResultOk ||
          info.channelCount != 2)
        throw std::runtime_error("Stereo VST3 buses required.");
      component->activateBus(kAudio, dir, 0, true);
      for (int i = 0; i < component->getBusCount(kEvent, dir); i++)
        component->activateBus(kEvent, dir, i, false);
    }
    if (processor->canProcessSampleSize(kSample32) != kResultTrue)
      throw std::runtime_error("VST3 requires unsupported sample precision.");
    ProcessSetup setup{kRealtime, kSample32, block, rate};
    if (processor->setupProcessing(setup) != kResultOk)
      throw std::runtime_error("VST3 processing setup failed.");
    left.resize(block);
    right.resize(block);
    outLeft.resize(block);
    outRight.resize(block);
    if (component->setActive(true) != kResultOk)
      throw std::runtime_error("VST3 activation failed.");
    active = true;
    if (processor->setProcessing(true) != kResultOk)
      throw std::runtime_error("VST3 processing could not start.");
    processing = true;
  }
  ~Instance() {
    closeEditor();
    if (processing)
      processor->setProcessing(false);
    if (active)
      component->setActive(false);
    if (from && to) {
      from->disconnect(to);
      to->disconnect(from);
    }
    if (from)
      from->release();
    if (to)
      to->release();
    if (controller) {
      controller->setComponentHandler(nullptr);
      if (controllerInit)
        controller->terminate();
      controller->release();
    }
    if (processor)
      processor->release();
    if (component) {
      if (initialized)
        component->terminate();
      component->release();
    }
    editor.clear();
    module.reset(); // Factory teardown may still call the live host context.
  }
  void closeEditor() {
    if (view) {
      if (attached) view->removed();
      attached = false; view->setFrame(nullptr); view->release(); view = nullptr;
      editor.view = nullptr;
    }
  }
  void openEditor(uintptr_t parent, double scale) {
    closeEditor();
    if (!controller || !parent || !(view = controller->createView(ViewType::kEditor)))
      throw std::runtime_error("This plug-in has no custom editor. Use its parameter controls.");
    if (view->isPlatformTypeSupported(kPlatformTypeX11EmbedWindowID) != kResultTrue) {
      closeEditor(); throw std::runtime_error("This plug-in editor does not support Linux X11/XWayland.");
    }
    editor.view = view; view->setFrame(&editor);
    IPlugViewContentScaleSupport* scaling = nullptr;
    if (view->queryInterface(IPlugViewContentScaleSupport::iid, (void**)&scaling) == kResultOk && scaling) {
      scaling->setContentScaleFactor(scale); scaling->release();
    }
    ViewRect size;
    if (view->getSize(&size) != kResultOk || size.getWidth() < 16 || size.getHeight() < 16 || size.getWidth() > 8192 || size.getHeight() > 8192) {
      closeEditor(); throw std::runtime_error("The plug-in editor returned an invalid window size.");
    }
    editor.width = size.getWidth(); editor.height = size.getHeight();
    if (view->attached(reinterpret_cast<void*>(parent), kPlatformTypeX11EmbedWindowID) != kResultOk) {
      closeEditor(); throw std::runtime_error("The plug-in editor could not open. Use its parameter controls.");
    }
    attached = true; view->onSize(&size);
  }
  void process(float *interleaved, int frames) {
    if (frames < 0 || frames > block)
      throw std::runtime_error("Invalid VST3 block size.");
    for (int i = 0; i < frames; i++) {
      left[i] = interleaved[2 * i];
      right[i] = interleaved[2 * i + 1];
      outLeft[i] = outRight[i] = 0;
    }
    float *in[] = {left.data(), right.data()},
          *out[] = {outLeft.data(), outRight.data()};
    AudioBusBuffers input, output;
    input.numChannels = output.numChannels = 2;
    input.channelBuffers32 = in;
    output.channelBuffers32 = out;
    ProcessContext context{};
    context.sampleRate = rate;
    context.projectTimeSamples = position;
    context.state = ProcessContext::kPlaying | ProcessContext::kTempoValid |
                    ProcessContext::kTimeSigValid;
    context.tempo = 120;
    context.timeSigNumerator = 4;
    context.timeSigDenominator = 4;
    ProcessData data;
    data.processMode = kRealtime;
    data.numSamples = frames;
    data.numInputs = data.numOutputs = 1;
    data.inputs = &input;
    data.outputs = &output;
    data.inputParameterChanges = &pending;
    data.processContext = &context;
    if (processor->process(data) != kResultOk)
      throw std::runtime_error("The VST3 effect rejected an audio block.");
    pending.values.clear();
    position += frames;
    for (int i = 0; i < frames; i++) {
      if (!std::isfinite(outLeft[i]) || !std::isfinite(outRight[i]))
        throw std::runtime_error("Non-finite VST3 output.");
      interleaved[2 * i] = outLeft[i];
      interleaved[2 * i + 1] = outRight[i];
    }
  }
};
int copyText(const std::string &s, char *out, int capacity) {
  if (s.size() + 1 > size_t(capacity))
    throw std::runtime_error("VST3 metadata exceeds buffer limit.");
  std::memcpy(out, s.c_str(), s.size() + 1);
  return s.size();
}
} // namespace
extern "C" {
const char *ss_vst_error() { return error.c_str(); }
int ss_vst_scan(const char *path, char *out, int capacity) {
  try {
    Module module(path);
    std::string s = "[";
    int count = module.factory->countClasses();
    if (count < 0 || count > 4096)
      throw std::runtime_error("Invalid VST3 class count.");
    bool comma = false;
    for (int i = 0; i < count; i++) {
      PClassInfo info{};
      if (module.factory->getClassInfo(i, &info) != kResultOk ||
          std::strcmp(info.category, kVstAudioEffectClass))
        continue;
      FUID id(info.cid);
      char cid[33];
      id.toString(cid);
      if (comma)
        s += ',';
      comma = true;
      s +=
          "{\"id\":" + quote(cid) + ",\"name\":" +
          quote(std::string(info.name, strnlen(info.name, sizeof(info.name)))) +
          "}";
    }
    return copyText(s + "]", out, capacity);
  } catch (const std::exception &e) {
    error = e.what();
    return -1;
  }
}
void *ss_vst_open(const char *path, const char *id, double rate) {
  try {
    if (!std::isfinite(rate) || rate < 1000 || rate > 384000)
      throw std::runtime_error("Invalid VST3 rate.");
    auto instance = std::make_unique<Instance>(path, id, rate);
    instance->setup();
    return instance.release();
  } catch (const std::exception &e) {
    error = e.what();
    return nullptr;
  }
}
void ss_vst_close(void *handle) { delete static_cast<Instance *>(handle); }
uint32 ss_vst_latency(void* handle) { return static_cast<Instance*>(handle)->processor->getLatencySamples(); }
int ss_vst_editor_open(void* handle, uintptr_t parent, double scale) {
  try { static_cast<Instance*>(handle)->openEditor(parent, scale); return 0; }
  catch (const std::exception& e) { error = e.what(); return -1; }
}
void ss_vst_editor_close(void* handle) { static_cast<Instance*>(handle)->closeEditor(); }
int ss_vst_editor_size(void* handle, int* width, int* height) {
  auto* p = static_cast<Instance*>(handle); *width = p->editor.width; *height = p->editor.height;
  return p->view ? 1 : 0;
}
int ss_vst_editor_resize(void* handle, int width, int height) {
  try {
    auto* p = static_cast<Instance*>(handle);
    if (!p->view || width < 16 || height < 16 || width > 8192 || height > 8192) return -1;
    if (p->view->canResize() != kResultTrue) return 0;
    ViewRect size(0, 0, width, height); p->view->checkSizeConstraint(&size);
    return p->editor.resizeView(p->view, &size) == kResultOk ? 0 : -1;
  } catch (const std::exception& e) { error = e.what(); return -1; }
}
int ss_vst_editor_idle(void* handle) {
  try { static_cast<Instance*>(handle)->editor.tick(); return 0; }
  catch (const std::exception& e) { error = e.what(); return -1; }
}
int ss_vst_process(void *handle, float *data, int frames) {
  try {
    static_cast<Instance *>(handle)->process(data, frames);
    return 0;
  } catch (const std::exception &e) {
    error = e.what();
    return -1;
  }
}
int ss_vst_set(void *handle, uint32 id, double value) {
  try {
    auto *p = static_cast<Instance *>(handle);
    if (!std::isfinite(value) || value < 0 || value > 1)
      throw std::runtime_error("Invalid normalized parameter.");
    if (!p->controller)
      throw std::runtime_error("VST3 has no parameter controller.");
    if (p->controller->setParamNormalized(id, value) != kResultOk)
      throw std::runtime_error("VST3 rejected a parameter.");
    int32 index;
    auto *q = p->pending.addParameterData(id, index);
    if (!q)
      throw std::runtime_error("Too many VST3 parameters.");
    q->addPoint(0, value, index);
    return 0;
  } catch (const std::exception &e) {
    error = e.what();
    return -1;
  }
}
int ss_vst_info(void *handle, char *out, int capacity) {
  try {
    auto *p = static_cast<Instance *>(handle);
    std::string s =
        "{\"latency\":" + std::to_string(p->processor->getLatencySamples()) +
        ",\"parameters\":[";
    int count = p->controller ? p->controller->getParameterCount() : 0;
    if (count < 0 || count > 4096)
      throw std::runtime_error("Too many VST3 parameters.");
    bool comma = false;
    for (int i = 0; i < count; i++) {
      ParameterInfo info{};
      if (p->controller->getParameterInfo(i, info) != kResultOk)
        continue;
      if (comma)
        s += ',';
      comma = true;
      s += "{\"id\":" + std::to_string(info.id) +
           ",\"name\":" + quote(utf8(info.title)) +
           ",\"unit\":" + quote(utf8(info.units)) +
           ",\"steps\":" + std::to_string(info.stepCount) + ",\"readonly\":" +
           (info.flags & ParameterInfo::kIsReadOnly ? "true" : "false") +
           ",\"value\":" +
           decimal(p->controller->getParamNormalized(info.id)) + "}";
    }
    return copyText(s + "]}", out, capacity);
  } catch (const std::exception &e) {
    error = e.what();
    return -1;
  }
}
int ss_vst_state(void *handle, void *out, int capacity) {
  try {
    auto *p = static_cast<Instance *>(handle);
    Stream state;
    if (p->component->getState(&state) != kResultOk)
      return 0;
    if (state.failed || state.bytes.size() > size_t(capacity))
      throw std::runtime_error("VST3 state exceeds 1 MiB.");
    std::memcpy(out, state.bytes.data(), state.bytes.size());
    return state.bytes.size();
  } catch (const std::exception &e) {
    error = e.what();
    return -1;
  }
}
int ss_vst_restore(void *handle, const void *data, int bytes) {
  try {
    if (bytes < 0 || bytes > int(maxState))
      throw std::runtime_error("Invalid VST3 state size.");
    auto *p = static_cast<Instance *>(handle);
    Stream state;
    state.bytes.assign((const char *)data, (const char *)data + bytes);
    p->processor->setProcessing(false);
    p->processing = false;
    p->component->setActive(false);
    p->active = false;
    if (bytes && p->component->setState(&state) != kResultOk)
      throw std::runtime_error("VST3 state restoration failed.");
    state.pos = 0;
    if (bytes && p->controller)
      p->controller->setComponentState(&state);
    if (p->component->setActive(true) != kResultOk)
      throw std::runtime_error(
          "VST3 could not reactivate after restoring state.");
    p->active = true;
    if (p->processor->setProcessing(true) != kResultOk)
      throw std::runtime_error("VST3 could not resume after restoring state.");
    p->processing = true;
    return 0;
  } catch (const std::exception &e) {
    error = e.what();
    return -1;
  }
}
}

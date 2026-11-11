// Independent ABI fixture: a stereo gain plug-in with separate control/DSP
// values.
#define INIT_CLASS_IID
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstaudioprocessor.h"
#include "pluginterfaces/vst/ivsteditcontroller.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
#include <algorithm>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
using namespace Steinberg;
using namespace Steinberg::Vst;
static FUID classId(0xABCDEF01, 0x12345678, 0x10203040, 0x55667788);
static bool entered = false;
static bool equal(const TUID a, const FUID &b) {
  return std::memcmp(a, b.toTUID(), 16) == 0;
}
class Gain final : public IComponent,
                   public IAudioProcessor,
                   public IEditController {
  uint32 refs = 1;
  double value = .5, gain = 1, crash = 0, slow = 0;
  bool active = false, processing = false;

public:
  tresult PLUGIN_API queryInterface(const TUID id, void **obj) override {
    if (equal(id, IComponent::iid) || equal(id, FUnknown::iid))
      *obj = static_cast<IComponent *>(this);
    else if (equal(id, IAudioProcessor::iid))
      *obj = static_cast<IAudioProcessor *>(this);
    else if (equal(id, IEditController::iid))
      *obj = static_cast<IEditController *>(this);
    else {
      *obj = nullptr;
      return kNoInterface;
    }
    addRef();
    return kResultOk;
  }
  uint32 PLUGIN_API addRef() override { return ++refs; }
  uint32 PLUGIN_API release() override {
    auto n = --refs;
    if (!n)
      delete this;
    return n;
  }
  tresult PLUGIN_API initialize(FUnknown *host) override {
    return host ? kResultOk : kInvalidArgument;
  }
  tresult PLUGIN_API terminate() override { return kResultOk; }
  tresult PLUGIN_API getControllerClassId(TUID id) override {
    classId.toTUID(id);
    return kResultOk;
  }
  tresult PLUGIN_API setIoMode(IoMode) override { return kResultOk; }
  int32 PLUGIN_API getBusCount(MediaType type, BusDirection) override {
    return type == kAudio ? 1 : 0;
  }
  tresult PLUGIN_API getBusInfo(MediaType type, BusDirection dir, int32 index,
                                BusInfo &info) override {
    if (type != kAudio || index)
      return kInvalidArgument;
    info = {};
    info.mediaType = type;
    info.direction = dir;
    info.channelCount = 2;
    info.busType = kMain;
    return kResultOk;
  }
  tresult PLUGIN_API getRoutingInfo(RoutingInfo &, RoutingInfo &) override {
    return kNotImplemented;
  }
  tresult PLUGIN_API activateBus(MediaType, BusDirection, int32,
                                 TBool) override {
    return kResultOk;
  }
  tresult PLUGIN_API setActive(TBool v) override {
    active = v;
    return kResultOk;
  }
  tresult PLUGIN_API setState(IBStream *state) override {
    int32 n = 0;
    if (state->read(&gain, sizeof(gain), &n) != kResultOk || n != sizeof(gain))
      return kResultFalse;
    value = gain / 2;
    return kResultOk;
  }
  tresult PLUGIN_API getState(IBStream *state) override {
    return state->write(&gain, sizeof(gain));
  }
  tresult PLUGIN_API setBusArrangements(SpeakerArrangement *in, int32 ni,
                                        SpeakerArrangement *out,
                                        int32 no) override {
    return ni == 1 && no == 1 && in[0] == SpeakerArr::kStereo &&
                   out[0] == SpeakerArr::kStereo
               ? kResultTrue
               : kResultFalse;
  }
  tresult PLUGIN_API getBusArrangement(BusDirection, int32 index,
                                       SpeakerArrangement &arr) override {
    arr = SpeakerArr::kStereo;
    return index ? kInvalidArgument : kResultOk;
  }
  tresult PLUGIN_API canProcessSampleSize(int32 size) override {
    return size == kSample32 ? kResultTrue : kResultFalse;
  }
  uint32 PLUGIN_API getLatencySamples() override { return 0; }
  tresult PLUGIN_API setupProcessing(ProcessSetup &setup) override {
    return setup.maxSamplesPerBlock == 1024 && setup.sampleRate > 0
               ? kResultOk
               : kInvalidArgument;
  }
  tresult PLUGIN_API setProcessing(TBool v) override {
    processing = v;
    return kResultOk;
  }
  tresult PLUGIN_API process(ProcessData &data) override {
    if (!active || !processing)
      return kResultFalse;
    if (data.inputParameterChanges)
      for (int i = 0; i < data.inputParameterChanges->getParameterCount();
           i++) {
        auto *q = data.inputParameterChanges->getParameterData(i);
        int32 offset;
        double v;
        if (q->getPoint(q->getPointCount() - 1, offset, v) == kResultOk) {
          if (q->getParameterId() == 0)
            gain = v * 2;
          if (q->getParameterId() == 3)
            crash = v;
          if (q->getParameterId() == 4)
            slow = v;
        }
      }
    if (crash > .99)
      std::abort();
    if (slow > .99)
      usleep(5000000);
    for (int c = 0; c < 2; c++)
      for (int i = 0; i < data.numSamples; i++)
        data.outputs[0].channelBuffers32[c][i] =
            float(data.inputs[0].channelBuffers32[c][i] * gain);
    return kResultOk;
  }
  uint32 PLUGIN_API getTailSamples() override { return 0; }
  tresult PLUGIN_API setComponentState(IBStream *state) override {
    return setState(state);
  }
  int32 PLUGIN_API getParameterCount() override { return 3; }
  tresult PLUGIN_API getParameterInfo(int32 index,
                                      ParameterInfo &info) override {
    if (index < 0 || index >= 3)
      return kInvalidArgument;
    info = {};
    info.id = index == 0 ? 0 : index == 1 ? 3 : 4;
    info.defaultNormalizedValue = index ? 0 : .5;
    const char *label = index == 0   ? "Gain"
                        : index == 1 ? "Crash test"
                                     : "Timeout test";
    for (int i = 0; label[i]; i++)
      info.title[i] = label[i];
    return kResultOk;
  }
  tresult PLUGIN_API getParamStringByValue(ParamID, ParamValue,
                                           String128) override {
    return kNotImplemented;
  }
  tresult PLUGIN_API getParamValueByString(ParamID, TChar *,
                                           ParamValue &) override {
    return kNotImplemented;
  }
  ParamValue PLUGIN_API normalizedParamToPlain(ParamID, ParamValue v) override {
    return v * 2;
  }
  ParamValue PLUGIN_API plainParamToNormalized(ParamID, ParamValue v) override {
    return v / 2;
  }
  ParamValue PLUGIN_API getParamNormalized(ParamID id) override {
    return id == 0 ? value : id == 3 ? crash : slow;
  }
  tresult PLUGIN_API setParamNormalized(ParamID id, ParamValue v) override {
    if (id == 0)
      value = v;
    return kResultOk;
  }
  tresult PLUGIN_API setComponentHandler(IComponentHandler *) override {
    return kResultOk;
  }
  IPlugView *PLUGIN_API createView(FIDString) override { return nullptr; }
};
class Factory final : public IPluginFactory {
public:
  tresult PLUGIN_API queryInterface(const TUID id, void **obj) override {
    if (equal(id, IPluginFactory::iid) || equal(id, FUnknown::iid)) {
      *obj = this;
      return kResultOk;
    }
    *obj = nullptr;
    return kNoInterface;
  }
  uint32 PLUGIN_API addRef() override { return 1; }
  uint32 PLUGIN_API release() override { return 1; }
  tresult PLUGIN_API getFactoryInfo(PFactoryInfo *info) override {
    *info = {};
    std::strcpy(info->vendor, "SoundSausage fixture");
    return kResultOk;
  }
  int32 PLUGIN_API countClasses() override { return 1; }
  tresult PLUGIN_API getClassInfo(int32 index, PClassInfo *info) override {
    if (index)
      return kInvalidArgument;
    *info = {};
    classId.toTUID(info->cid);
    info->cardinality = PClassInfo::kManyInstances;
    std::strcpy(info->category, kVstAudioEffectClass);
    std::strcpy(info->name, "SoundSausage Test Gain");
    return kResultOk;
  }
  tresult PLUGIN_API createInstance(FIDString cid, FIDString id,
                                    void **obj) override {
    if (!equal(cid, classId))
      return kNoInterface;
    auto *gain = new Gain;
    auto result = gain->queryInterface(id, obj);
    gain->release();
    return result;
  }
};
extern "C" bool ModuleEntry(void *) {
  entered = true;
  return true;
}
extern "C" bool ModuleExit() {
  entered = false;
  return true;
}
extern "C" IPluginFactory *GetPluginFactory() {
  static Factory factory;
  return entered ? &factory : nullptr;
}

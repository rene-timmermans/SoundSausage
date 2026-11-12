// Linux VST3 editor services. Owned and called by the isolated helper's GUI thread.
class EditorFrame final : public IPlugFrame, public Linux::IRunLoop {
  using Clock = std::chrono::steady_clock;
  struct Timer { Linux::TimerInterval interval; Clock::time_point due; };
  std::map<int, Linux::IEventHandler*> descriptors;
  std::map<Linux::ITimerHandler*, Timer> timers;
public:
  IPlugView* view = nullptr;
  int width = 640, height = 480;
  uint32 PLUGIN_API addRef() override { return 1; }
  uint32 PLUGIN_API release() override { return 1; }
  tresult PLUGIN_API queryInterface(const TUID id, void** object) override {
    *object = nullptr;
    if (equal(id, IPlugFrame::iid) || equal(id, FUnknown::iid)) *object = static_cast<IPlugFrame*>(this);
    else if (equal(id, Linux::IRunLoop::iid)) *object = static_cast<Linux::IRunLoop*>(this);
    return *object ? kResultOk : kNoInterface;
  }
  tresult PLUGIN_API resizeView(IPlugView* source, ViewRect* size) override {
    if (!size || source != view || size->getWidth() < 16 || size->getHeight() < 16 ||
        size->getWidth() > 8192 || size->getHeight() > 8192) return kInvalidArgument;
    width = size->getWidth(); height = size->getHeight();
    return view->onSize(size);
  }
  tresult PLUGIN_API registerEventHandler(Linux::IEventHandler* handler, int fd) override {
    if (!handler || fd < 0 || descriptors.size() >= 512) return kInvalidArgument;
    auto found = descriptors.find(fd);
    handler->addRef();
    if (found != descriptors.end()) found->second->release();
    descriptors[fd] = handler; return kResultOk;
  }
  tresult PLUGIN_API unregisterEventHandler(Linux::IEventHandler* handler) override {
    for (auto it = descriptors.begin(); it != descriptors.end();) {
      if (it->second == handler) { it = descriptors.erase(it); handler->release(); }
      else ++it;
    }
    return kResultOk;
  }
  tresult PLUGIN_API registerTimer(Linux::ITimerHandler* handler, Linux::TimerInterval ms) override {
    if (!handler || !ms || ms > 3600000 || timers.size() >= 512) return kInvalidArgument;
    if (!timers.count(handler)) handler->addRef();
    timers[handler] = {ms, Clock::now() + std::chrono::milliseconds(ms)};
    return kResultOk;
  }
  tresult PLUGIN_API unregisterTimer(Linux::ITimerHandler* handler) override {
    if (timers.erase(handler)) handler->release();
    return kResultOk;
  }
  void tick() {
    // Retain snapshots: plug-ins may unregister their handlers inside callbacks.
    std::vector<std::pair<int, Linux::IEventHandler*>> ready;
    for (auto [fd, handler] : descriptors) {
      pollfd item{fd, POLLIN, 0};
      if (::poll(&item, 1, 0) > 0 && (item.revents & POLLIN)) { handler->addRef(); ready.emplace_back(fd, handler); }
    }
    for (auto [fd, handler] : ready) {
      auto found = descriptors.find(fd);
      if (found != descriptors.end() && found->second == handler) handler->onFDIsSet(fd);
      handler->release();
    }
    std::vector<Linux::ITimerHandler*> due;
    auto now = Clock::now();
    for (auto& [handler, timer] : timers) if (timer.due <= now) {
      timer.due = now + std::chrono::milliseconds(timer.interval);
      handler->addRef(); due.push_back(handler);
    }
    for (auto* handler : due) { if (timers.count(handler)) handler->onTimer(); handler->release(); }
  }
  void clear() {
    auto old_descriptors = std::move(descriptors); descriptors.clear();
    auto old_timers = std::move(timers); timers.clear();
    for (auto [fd, handler] : old_descriptors) handler->release();
    for (auto [handler, timer] : old_timers) handler->release();
  }
  ~EditorFrame() { clear(); }
};

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>

// All buffers are interleaved float32. The caller owns allocation and lifetime.
// No exceptions, allocations, host callbacks, or global mutable state cross this ABI.
extern "C" {

std::uint32_t ce_dsp_abi_version() noexcept { return 3; }

static bool valid_buffer(float* data, std::size_t frames, std::size_t channels) noexcept {
    return channels >= 1 && channels <= 2 &&
           frames <= std::numeric_limits<std::size_t>::max() / channels &&
           (data != nullptr || frames == 0);
}

int ce_gain(float* data, std::size_t frames, std::size_t channels,
            const double* initial, const double* final, int logarithmic) noexcept {
    if (!valid_buffer(data, frames, channels) || !initial || !final) return -1;
    for (std::size_t c = 0; c < channels; ++c) {
        if (!std::isfinite(initial[c]) || !std::isfinite(final[c]) ||
            initial[c] < 0 || final[c] < 0 || initial[c] > 1000 || final[c] > 1000)
            return -1;
        if (logarithmic && (initial[c] <= 0 || final[c] <= 0)) return -1;
    }
    for (std::size_t f = 0; f < frames; ++f) {
        const double t = frames > 1 ? static_cast<double>(f) / (frames - 1) : 0;
        for (std::size_t c = 0; c < channels; ++c) {
            const double gain = logarithmic
                ? std::exp(std::log(initial[c]) + t * (std::log(final[c]) - std::log(initial[c])))
                : initial[c] + t * (final[c] - initial[c]);
            data[f * channels + c] = static_cast<float>(data[f * channels + c] * gain);
        }
    }
    return 0;
}

int ce_normalize(float* data, std::size_t frames, std::size_t channels,
                 double target, int linked) noexcept {
    if (!valid_buffer(data, frames, channels) || !std::isfinite(target) ||
        target < 0 || target > 1) return -1;
    double peaks[2] = {0, 0};
    for (std::size_t f = 0; f < frames; ++f)
        for (std::size_t c = 0; c < channels; ++c)
            peaks[c] = std::max(peaks[c], std::abs(static_cast<double>(data[f * channels + c])));
    if (linked && channels == 2) peaks[0] = peaks[1] = std::max(peaks[0], peaks[1]);
    for (std::size_t f = 0; f < frames; ++f)
        for (std::size_t c = 0; c < channels; ++c)
            if (peaks[c] > 0)
                data[f * channels + c] = static_cast<float>(data[f * channels + c] * target / peaks[c]);
    return 0;
}

int ce_reverse(float* data, std::size_t frames, std::size_t channels) noexcept {
    if (!valid_buffer(data, frames, channels)) return -1;
    for (std::size_t f = 0; f < frames / 2; ++f)
        for (std::size_t c = 0; c < channels; ++c)
            std::swap(data[f * channels + c], data[(frames - 1 - f) * channels + c]);
    return 0;
}

int ce_invert(float* data, std::size_t frames, std::size_t channels) noexcept {
    if (!valid_buffer(data, frames, channels)) return -1;
    for (std::size_t i = 0; i < frames * channels; ++i) data[i] = -data[i];
    return 0;
}

int ce_silence(float* data, std::size_t frames, std::size_t channels) noexcept {
    if (!valid_buffer(data, frames, channels)) return -1;
    std::fill_n(data, frames * channels, 0.0f);
    return 0;
}

int ce_mix_add(float* output, std::size_t output_frames,
               const float* source, std::size_t source_frames, std::size_t source_channels,
               std::size_t output_offset, std::size_t clip_offset, std::size_t clip_frames,
               std::size_t fade_in, std::size_t fade_out, double left, double right) noexcept {
    if (!valid_buffer(output, output_frames, 2) ||
        !valid_buffer(const_cast<float*>(source), source_frames, source_channels) ||
        output_offset > output_frames || source_frames > output_frames - output_offset ||
        clip_offset > clip_frames || source_frames > clip_frames - clip_offset ||
        fade_in > clip_frames || fade_out > clip_frames - fade_in ||
        !std::isfinite(left) || !std::isfinite(right) ||
        left < 0 || right < 0 || left > 10000 || right > 10000) return -1;
    for (std::size_t f = 0; f < source_frames; ++f) {
        const auto position = clip_offset + f;
        double envelope = 1;
        if (fade_in && position < fade_in)
            envelope *= fade_in > 1 ? static_cast<double>(position) / (fade_in - 1) : 0;
        if (fade_out && position >= clip_frames - fade_out)
            envelope *= fade_out > 1 ? static_cast<double>(clip_frames - 1 - position) / (fade_out - 1) : 0;
        const float l = source[f * source_channels];
        const float r = source[f * source_channels + (source_channels == 2 ? 1 : 0)];
        output[(output_offset + f) * 2] += static_cast<float>(l * left * envelope);
        output[(output_offset + f) * 2 + 1] += static_cast<float>(r * right * envelope);
    }
    return 0;
}

struct EnvelopePoint {
    std::uint64_t frame;
    double value;
};

static bool valid_curve(const EnvelopePoint* points, std::size_t count, double low, double high) noexcept {
    if (count > 512 || (count && !points)) return false;
    for (std::size_t i = 0; i < count; ++i)
        if (!std::isfinite(points[i].value) || points[i].value < low || points[i].value > high ||
            (i && points[i].frame <= points[i - 1].frame)) return false;
    return true;
}

static double curve_value(const EnvelopePoint* points, std::size_t count, std::size_t& index,
                          std::uint64_t frame, double neutral) noexcept {
    if (!count) return neutral;
    while (index + 1 < count && points[index + 1].frame <= frame) ++index;
    if (frame <= points[0].frame) return points[0].value;
    if (index + 1 == count) return points[index].value;
    const auto& a = points[index];
    const auto& b = points[index + 1];
    const double t = static_cast<double>(frame - a.frame) / (b.frame - a.frame);
    return a.value + (b.value - a.value) * t;
}

int ce_mix_add_automated(float* output, std::size_t output_frames,
               const float* source, std::size_t source_frames, std::size_t source_channels,
               std::size_t output_offset, std::size_t clip_offset, std::size_t clip_frames,
               std::size_t fade_in, std::size_t fade_out, double left, double right,
               std::uint64_t source_offset,
               const EnvelopePoint* volume, std::size_t volume_count,
               const EnvelopePoint* pan, std::size_t pan_count) noexcept {
    if (!valid_buffer(output, output_frames, 2) ||
        !valid_buffer(const_cast<float*>(source), source_frames, source_channels) ||
        output_offset > output_frames || source_frames > output_frames - output_offset ||
        clip_offset > clip_frames || source_frames > clip_frames - clip_offset ||
        source_frames > std::numeric_limits<std::uint64_t>::max() - source_offset ||
        fade_in > clip_frames || fade_out > clip_frames - fade_in ||
        !std::isfinite(left) || !std::isfinite(right) || left < 0 || right < 0 || left > 10000 || right > 10000 ||
        !valid_curve(volume, volume_count, 0, 2) || !valid_curve(pan, pan_count, -1, 1)) return -1;
    std::size_t vi = 0, pi = 0;
    for (std::size_t f = 0; f < source_frames; ++f) {
        const auto position = clip_offset + f;
        double envelope = curve_value(volume, volume_count, vi, source_offset + f, 1);
        const double balance = curve_value(pan, pan_count, pi, source_offset + f, 0);
        if (fade_in && position < fade_in)
            envelope *= fade_in > 1 ? static_cast<double>(position) / (fade_in - 1) : 0;
        if (fade_out && position >= clip_frames - fade_out)
            envelope *= fade_out > 1 ? static_cast<double>(clip_frames - 1 - position) / (fade_out - 1) : 0;
        const float l = source[f * source_channels];
        const float r = source[f * source_channels + (source_channels == 2 ? 1 : 0)];
        output[(output_offset + f) * 2] += static_cast<float>(l * left * envelope * (1 - std::max(0.0, balance)));
        output[(output_offset + f) * 2 + 1] += static_cast<float>(r * right * envelope * (1 + std::min(0.0, balance)));
    }
    return 0;
}

}

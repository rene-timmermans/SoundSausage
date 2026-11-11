#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>

// All buffers are interleaved float32. The caller owns allocation and lifetime.
// No exceptions, allocations, host callbacks, or global mutable state cross this ABI.
extern "C" {

std::uint32_t ce_dsp_abi_version() noexcept { return 6; }

static bool valid_buffer(float* data, std::size_t frames, std::size_t channels) noexcept {
    return channels >= 1 && channels <= 2 &&
           frames <= std::numeric_limits<std::size_t>::max() / channels &&
           (data != nullptr || frames == 0);
}

// Normalized biquads [b0,b1,b2,a1,a2], transposed direct form II.
// State is caller-owned [stage][channel][z1,z2] and survives block boundaries.
int ce_biquads(float* data, std::size_t frames, std::size_t channels,
               const double* coefficients, std::size_t stages, double* state,
               double gain) noexcept {
    if (!valid_buffer(data, frames, channels) || stages > 64 ||
        (stages && (!coefficients || !state)) || !std::isfinite(gain) || gain < 0 || gain > 16) return -1;
    for (std::size_t s = 0; s < stages; ++s) {
        const double* k = coefficients + 5*s;
        for (std::size_t j = 0; j < 5; ++j) if (!std::isfinite(k[j])) return -1;
        if (std::abs(k[4]) >= 1 || 1+k[3]+k[4] <= 0 || 1-k[3]+k[4] <= 0) return -1;
        for (std::size_t j = 0; j < 2*channels; ++j)
            if (!std::isfinite(state[s*channels*2+j])) return -1;
    }
    for (std::size_t f = 0; f < frames; ++f) {
        for (std::size_t c = 0; c < channels; ++c) {
            double x = data[f*channels+c];
            for (std::size_t s = 0; s < stages; ++s) {
                const double* k = coefficients + 5*s;
                double* z = state + (s*channels+c)*2;
                const double y = k[0]*x + z[0];
                z[0] = k[1]*x - k[3]*y + z[1];
                z[1] = k[2]*x - k[4]*y;
                // Prevent slow denormal arithmetic during long silent tails.
                if (std::abs(z[0]) < 1e-300) z[0] = 0;
                if (std::abs(z[1]) < 1e-300) z[1] = 0;
                x = y;
            }
            const double y = x*gain;
            if (!std::isfinite(y) || std::abs(y) > std::numeric_limits<float>::max()) return -2;
            data[f*channels+c] = static_cast<float>(y);
        }
    }
    return 0;
}

int ce_gain(float* data, std::size_t frames, std::size_t channels,
            const double* initial, const double* final, int logarithmic,
            std::size_t offset, std::size_t total) noexcept {
    if (!valid_buffer(data, frames, channels) || !initial || !final || offset > total || frames > total-offset) return -1;
    for (std::size_t c = 0; c < channels; ++c) {
        if (!std::isfinite(initial[c]) || !std::isfinite(final[c]) ||
            initial[c] < 0 || final[c] < 0 || initial[c] > 1000 || final[c] > 1000)
            return -1;
        if (logarithmic && (initial[c] <= 0 || final[c] <= 0)) return -1;
    }
    for (std::size_t f = 0; f < frames; ++f) {
        const double t = total > 1 ? static_cast<double>(offset + f) / (total - 1) : 0;
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
                 double target, int linked, int remove_dc) noexcept {
    if (!valid_buffer(data, frames, channels) || !std::isfinite(target) ||
        target < 0 || target > 1) return -1;
    double means[2] = {0, 0}, peaks[2] = {0, 0};
    if (remove_dc && frames) {
        for (std::size_t f = 0; f < frames; ++f)
            for (std::size_t c = 0; c < channels; ++c)
                means[c] += data[f * channels + c];
        for (std::size_t c = 0; c < channels; ++c) means[c] /= frames;
    }
    for (std::size_t f = 0; f < frames; ++f)
        for (std::size_t c = 0; c < channels; ++c)
            peaks[c] = std::max(peaks[c], std::abs(static_cast<double>(data[f * channels + c]) - means[c]));
    if (linked && channels == 2) peaks[0] = peaks[1] = std::max(peaks[0], peaks[1]);
    for (std::size_t f = 0; f < frames; ++f)
        for (std::size_t c = 0; c < channels; ++c)
            if (peaks[c] > 0)
                data[f * channels + c] = static_cast<float>((data[f * channels + c] - means[c]) * target / peaks[c]);
            else if (remove_dc) data[f * channels + c] = 0;
    return 0;
}

int ce_channel_mix(float* data, std::size_t frames, std::size_t channels,
                   double ll, double lr, double rl, double rr) noexcept {
    if (!valid_buffer(data, frames, channels) || channels != 2) return -1;
    for (double value : {ll, lr, rl, rr})
        if (!std::isfinite(value) || std::abs(value) > 2) return -1;
    for (std::size_t f = 0; f < frames; ++f) {
        const double l = data[2 * f], r = data[2 * f + 1];
        data[2 * f] = static_cast<float>(l * ll + r * lr);
        data[2 * f + 1] = static_cast<float>(l * rl + r * rr);
    }
    return 0;
}

struct EffectPoint { double position, value; };

static bool valid_effect_curve(const EffectPoint* points, std::size_t count,
                               double xmin, double xmax, double ymin, double ymax) noexcept {
    if (!points || count < 2 || count > 64) return false;
    for (std::size_t i = 0; i < count; ++i)
        if (!std::isfinite(points[i].position) || !std::isfinite(points[i].value) ||
            points[i].position < xmin || points[i].position > xmax ||
            points[i].value < ymin || points[i].value > ymax ||
            (i && points[i].position <= points[i - 1].position)) return false;
    return true;
}

static double effect_curve_value(const EffectPoint* points, std::size_t count,
                                  double position, bool logarithmic = false) noexcept {
    if (position <= points[0].position) return points[0].value;
    for (std::size_t i = 1; i < count; ++i) {
        if (position > points[i].position) continue;
        const auto& a = points[i - 1];
        const auto& b = points[i];
        const double t = (position - a.position) / (b.position - a.position);
        return logarithmic ? std::exp(std::log(a.value) + t * (std::log(b.value) - std::log(a.value)))
                           : a.value + t * (b.value - a.value);
    }
    return points[count - 1].value;
}

int ce_envelope(float* data, std::size_t frames, std::size_t channels,
                const EffectPoint* points, std::size_t count, int logarithmic,
                std::size_t offset, std::size_t total) noexcept {
    if (!valid_buffer(data, frames, channels) || !valid_effect_curve(points, count, 0, 1, 0, 2) || offset > total || frames > total-offset ||
        points[0].position != 0 || points[count - 1].position != 1) return -1;
    if (logarithmic)
        for (std::size_t i = 0; i < count; ++i) if (points[i].value <= 0) return -1;
    for (std::size_t f = 0; f < frames; ++f) {
        const double position = total > 1 ? static_cast<double>(offset + f) / (total - 1) : 0;
        const double gain = effect_curve_value(points, count, position, logarithmic);
        for (std::size_t c = 0; c < channels; ++c)
            data[f * channels + c] = static_cast<float>(data[f * channels + c] * gain);
    }
    return 0;
}

int ce_dynamics(float* data, std::size_t frames, std::size_t channels, double sample_rate,
                const EffectPoint* points, std::size_t count,
                double attack_ms, double release_ms, double makeup_db, int linked, double* envelope) noexcept {
    if (!valid_buffer(data, frames, channels) || !valid_effect_curve(points, count, -96, 0, -96, 24) || !envelope ||
        !std::isfinite(sample_rate) || sample_rate < 1000 || sample_rate > 384000 ||
        !std::isfinite(attack_ms) || attack_ms < 0 || attack_ms > 1000 ||
        !std::isfinite(release_ms) || release_ms < 0 || release_ms > 5000 ||
        !std::isfinite(makeup_db) || std::abs(makeup_db) > 24) return -1;
    const double attack = attack_ms ? std::exp(-1000 / (sample_rate * attack_ms)) : 0;
    const double release = release_ms ? std::exp(-1000 / (sample_rate * release_ms)) : 0;
    for (std::size_t f = 0; f < frames; ++f) {
        double peaks[2] = {std::abs(static_cast<double>(data[f * channels])), 0};
        if (channels == 2) peaks[1] = std::abs(static_cast<double>(data[f * channels + 1]));
        if (linked && channels == 2) peaks[0] = peaks[1] = std::max(peaks[0], peaks[1]);
        for (std::size_t c = 0; c < channels; ++c) {
            const double coefficient = peaks[c] > envelope[c] ? attack : release;
            envelope[c] = coefficient * envelope[c] + (1 - coefficient) * peaks[c];
            const double db = 20 * std::log10(std::max(envelope[c], 1e-12));
            // Below the curve keep a constant gain; above it continue the final slope.
            const double clamped = std::clamp(db, points[0].position, points[count - 1].position);
            double gain_db = effect_curve_value(points, count, clamped) - clamped + makeup_db;
            if (db > clamped) {
                const auto& a = points[count - 2];
                const auto& b = points[count - 1];
                gain_db += (db - clamped) * ((b.value - a.value) / (b.position - a.position) - 1);
            }
            data[f * channels + c] = static_cast<float>(data[f * channels + c] * std::pow(10, gain_db / 20));
        }
    }
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

import wave
import struct

with wave.open("debug_stt.wav", "rb") as w:
    frames = w.readframes(w.getnframes())
    samples = struct.unpack('<' + 'h' * (len(frames) // 2), frames)
    print(f"Total samples: {len(samples)}")
    print(f"First 20 samples: {samples[:20]}")
    zero_samples = sum(1 for s in samples if s == 0)
    print(f"Zero samples: {zero_samples}")
    max_amp = max(abs(s) for s in samples)
    print(f"Max amp: {max_amp}")
    
    # Calculate some energy distribution
    low_amp = sum(1 for s in samples if abs(s) < 10)
    print(f"Samples close to zero (<10): {low_amp} ({low_amp/len(samples)*100:.2f}%)")

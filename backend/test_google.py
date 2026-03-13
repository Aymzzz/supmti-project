import os, wave, struct

if os.path.exists("debug_stt.wav"):
    with wave.open("debug_stt.wav", "rb") as w:
        frames = w.readframes(w.getnframes())
        samples = struct.unpack('<' + 'h' * (len(frames) // 2), frames)
        
        print(f"Total samples: {len(samples)}")
        
        # Calculate zero crossings
        zero_crossings = 0
        for i in range(1, len(samples)):
            if (samples[i-1] >= 0 and samples[i] < 0) or (samples[i-1] < 0 and samples[i] >= 0):
                zero_crossings += 1
                
        print(f"Zero crossings: {zero_crossings} (rate: {zero_crossings/len(samples):.4f})")
        
        # Calculate average absolute amplitude
        avg_amp = sum(abs(s) for s in samples) / len(samples)
        print(f"Average absolute amplitude: {avg_amp:.2f}")
        
        # Find first non-zero chunk of 10 samples
        for i in range(0, len(samples) - 10, 10):
            chunk = samples[i:i+10]
            if any(abs(s) > 100 for s in chunk):
                print(f"First non-silent chunk at index {i}: {chunk}")
                break

import sys
import os
import re

def convert_to_srt(raw_text):
    lines = raw_text.strip().split('\n')
    srt_output = []
    index = 1
    
    # Pattern: [HH:MM:SS] Text
    pattern = re.compile(r'\[(\d{2}:\d{2}:\d{2})\]\s+(.*)')
    
    segments = []
    for line in lines:
        match = pattern.match(line)
        if match:
            time_str = match.group(1).replace(':', ',') + ',000' # Simple padding
            text = match.group(2)
            segments.append({'time': match.group(1), 'text': text})
    
    for i in range(len(segments)):
        start = segments[i]['time']
        # End is start of next or +3s for last
        if i + 1 < len(segments):
            end = segments[i+1]['time']
        else:
            # Simple offset for last line
            h, m, s = map(int, start.split(':'))
            s += 4
            if s >= 60:
                s -= 60
                m += 1
            if m >= 60:
                m -= 60
                h += 1
            end = f"{h:02d}:{m:02d}:{s:02d}"
        
        # Format SRT times
        start_srt = start.replace(':', ',') + ',000'
        if ',' not in start_srt: # Handle potential partial matches
             start_srt = start + ",000"
        
        end_srt = end.replace(':', ',') + ',000'
        
        srt_output.append(f"{index}")
        srt_output.append(f"{start} --> {end}")
        srt_output.append(f"{segments[i]['text']}")
        srt_output.append("")
        index += 1
        
    return "\n".join(srt_output)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reconstruct_srt.py 'raw_text'")
        sys.exit(1)
    
    txt = sys.argv[1]
    print(convert_to_srt(txt))

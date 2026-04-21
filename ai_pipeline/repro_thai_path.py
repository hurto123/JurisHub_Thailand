import cv2
import numpy as np
import os

def test_imread():
    # Create a dummy file with Thai name
    path = "ทดสอบ.jpg"
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    # Save using imencode/tofile
    _, buf = cv2.imencode(".jpg", img)
    buf.tofile(path)
    
    print(f"File created: {path}")
    
    # Try reading with imread
    read_img = cv2.imread(path)
    if read_img is None:
        print(f"❌ cv2.imread failed for '{path}'")
    else:
        print(f"✅ cv2.imread worked for '{path}'")
        
    # Try reading with imdecode
    try:
        file_bytes = np.fromfile(path, dtype=np.uint8)
        read_img_decode = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if read_img_decode is None:
            print(f"❌ cv2.imdecode failed for '{path}'")
        else:
            print(f"✅ cv2.imdecode worked for '{path}'")
    except Exception as e:
        print(f"💥 Exception during imdecode: {e}")
        
    # Cleanup
    if os.path.exists(path):
        os.remove(path)

if __name__ == "__main__":
    test_imread()

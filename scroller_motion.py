import cv2
import pyautogui
import numpy as np
import time

# ปรับค่าความไว (Sensitivity)
# ปรับตัวเลขนี้ตามสภาพแสงและระยะห่างของมือ
MIN_AREA = 5000       # ขนาดขั้นต่ำของ "วัตถุ" (มือ) ที่จะจับการเคลื่อนไหว
SWIPE_THRESHOLD = 50  # ระยะที่ต้องปัด (พิกเซล)

# ตั้งค่ากล้อง
cap = cv2.VideoCapture(0)

# ตัวตรวจจับการเคลื่อนไหว (Background Subtraction)
fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

prev_cy = None
last_scroll_time = time.time()
cooldown = 1.0

print("---------------------------------------")
print("AI Motion Scroller (No MediaPipe Version)")
print("สถานะ: ทำงานบน Python 3.14 ได้ (ใช้เพียง OpenCV)")
print("- โบกมือ/ปัดมือขึ้น: คลิปถัดไป (Next)")
print("- โบกมือ/ปัดมือลง: คลิปก่อนหน้า (Prev)")
print("- กด 'q' เพื่อออก")
print("---------------------------------------")

while True:
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    height, width, _ = frame.shape
    
    # 1. ทำ Background Subtraction เพื่อหาส่วนที่เคลื่อนไหว
    fgmask = fgbg.apply(frame)
    
    # 2. กรอง Noise ออก
    kernel = np.ones((5,5), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)
    fgmask = cv2.dilate(fgmask, kernel, iterations=2)
    
    # 3. หาขอบเขตของวัตถุที่เคลื่อนไหว (Contours)
    contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    current_time = time.time()
    
    if contours:
        # หาวัตถุที่ใหญ่ที่สุด (น่าจะเป็นมือเรา)
        largest_contour = max(contours, key=cv2.contourArea)
        
        if cv2.contourArea(largest_contour) > MIN_AREA:
            # หาจุดศูนย์กลางของวัตถุ
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                # วาดวงกลมและกรอบแสดงตำแหน่ง
                x, y, w, h = cv2.boundingRect(largest_contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

                if prev_cy is not None:
                    dy = cy - prev_cy
                    
                    if current_time - last_scroll_time > cooldown:
                        if dy < -SWIPE_THRESHOLD:
                            print(">> SWIPE UP -> NEXT")
                            pyautogui.press('down')
                            last_scroll_time = current_time
                        elif dy > SWIPE_THRESHOLD:
                            print("<< SWIPE DOWN -> PREV")
                            pyautogui.press('up')
                            last_scroll_time = current_time
                
                prev_cy = cy
    else:
        prev_cy = None

    # แสดงผล
    cv2.putText(frame, "Motion Scroller (No AI Model)", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    # แสดงหน้าจอตรวจจับ (ขาวดำ) และหน้าจริง
    cv2.imshow('Motion Detection (Mask)', fgmask)
    cv2.imshow('TikTok Control (Original)', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

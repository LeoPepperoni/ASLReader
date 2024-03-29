import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import time
import mediapipe as mp


def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image, results


def draw_landmarks(image, results):
    mp_drawing.draw_landmarks(image, results.face_landmarks)
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)


def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(132)
    face = np.array([[res.x, res.y, res.z] for res in results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(1404)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, face, lh, rh])


DATA_PATH = os.path.join('MP_Data')

# Actions we want to detect
actions = np.array(['hello', 'leo', 'my', 'name'])

no_sequences = 30
sequence_length = 30

for action in actions:
    for sequence in range(no_sequences):
        dir_path = os.path.join(DATA_PATH, action, str(sequence))
        os.makedirs(dir_path, exist_ok=True)  # This will create all required parent directories

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# Set mediapipe model
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    for action in actions:
        for sequence in range(no_sequences):
            for frame_num in range(sequence_length):

                # Read feed
                ret, frame = cap.read()

                # Make detections
                image, results = mediapipe_detection(frame, holistic)
                print(results)

                # Draw Landmarks
                draw_landmarks(image, results)

                if frame_num == 0:
                    cv2.putText(image, 'STARTING COLLECTION', (120, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2,
                                cv2.LINE_AA)
                    # Splitting the text into two lines with a smaller font size
                    cv2.putText(image, 'Collecting frames for {}'.format(action), (15, 12), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 255, 0), 1, cv2.LINE_AA)
                    cv2.putText(image, 'Video Number {}'.format(sequence), (15, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 255, 0), 1, cv2.LINE_AA)
                    cv2.waitKey(2000)
                else:
                    # Also split here for consistency
                    cv2.putText(image, 'Collecting frames for {}'.format(action), (15, 12), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 255, 0), 1, cv2.LINE_AA)
                    cv2.putText(image, 'Video Number {}'.format(sequence), (15, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 255, 0), 1, cv2.LINE_AA)

                keypoints = extract_keypoints(results)
                npy_path = os.path.join(DATA_PATH, action, str(sequence), str(frame_num))
                np.save(npy_path, keypoints)

                # Show Screen
                cv2.imshow('Feed', image)

                # Break gracefullyqq
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    cap.release()
    cv2.destroyAllWindows()

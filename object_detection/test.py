from TF_Detector import Detector
import cv2
import matplotlib.pyplot as plt
import numpy as np

myDetector = Detector()
#img = cv2.imread('/home/nickshu/Desktop/airsim_testImg.jpg',1)
img_CV2 = cv2.imread('./test_images/dog.jpg',cv2.IMREAD_COLOR)
img_PLT = cv2.cvtColor(img_CV2, cv2.COLOR_BGR2RGB)
#cv2.imshow('img',img_CV2)
#cv2.waitKey(0)
res = myDetector.run_inference_for_single_image(img_PLT,showFigs=True)

results_Classes = res['detection_classes']
results_Scores = res['detection_scores']
results_Boxes = res['detection_boxes']

# Box format
#   [box_top, box_left, box_bottom, box_right]
#   box_top (Lower y value)
#   box_bottom = (Higher y value)

print(res)
idx_res = np.where(results_Classes == 3)
firstIndex = idx_res[0][0]
obj_acc = results_Scores[firstIndex]*100
obj_box = results_Boxes[firstIndex]

print('The first index is %d' % firstIndex)
print(type(firstIndex))

print('Its accuracy is %.2f%%' % obj_acc)
print(type(obj_acc))
print("Box: "+ str(obj_box))

plt.show()
print("Code Ended.")
#
# import numpy as np
# L = np.array([0,4,3])
# itemIdx = np.where(L==3)
# print(itemIdx)

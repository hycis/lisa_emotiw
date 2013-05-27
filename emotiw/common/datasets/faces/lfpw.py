from helper import within_bounds
from faceimages import FaceImagesDataset
import os

class Lfpw(FaceImagesDataset):
    def __init__(self):
        super(Lfpw, self).__init__("Labeled Face Parts in the Wild",
                                    "faces/labeled_face_parts_in_the_wild/")

        point_names = ['right_eyebrow_outer_end', 'left_eyebrow_outer_end', 'right_eyebrow_inner_end', 
                        'left_eyebrow_inner_end', 'right_eyebrow_center_top', 'right_eyebrow_center_bottom', 
                        'left_eyebrow_center_top', 'left_eyebrow_center_bottom', 'right_eye_outer_corner', 
                        'left_eye_outer_corner', 'right_eye_inner_corner', 'left_eye_inner_corner', 
                        'right_eye_center_top', 'right_eye_center_bottom', 'left_eye_center_top', 
                        'left_eye_center_bottom', 'right_eye_pupil', 'left_eye_pupil', 'right_nostril' , 
                        'left_nostril', 'nose_center_top', 'nose_tip', 'right_mouth_outer_corner', 
                        'left_mouth_outer_corner', 'mouth_top_lip', 'mouth_top_lip_bottom', 'mouth_bottom_lip_top', 
                        'mouth_bottom_lip', 'right_ear_top', 'left_ear_top', 'right_ear_bottom', 'left_ear_bottom', 
                        'right_ear_canal', 'left_ear_canal', 'chin_center']

        self.lstImages = []
        self.keyPointsDict = []

        test_file = os.path.join(self.absolute_base_directory, 'test_with_ids.csv')
        train_file = os.path.join(self.absolute_base_directory, 'train_with_ids.csv')
        test_dir = os.path.join(self.absolute_base_directory, 'test/')
        train_dir = os.path.join(self.absolute_base_directory, 'train/')

        lastIndices = {test_file: 0, train_file: 0}

        for f in (test_file, train_file):
            ff = open(f)
            lines = ff.readlines()[1:] #skip the first line (metadata)
            point_entries = [x for x in [k.strip().split("\t") for k in lines] if x[2] == "average"]
            
            for entry_idx, entries in enumerate(point_entries):
                self.lstImages.append(entries[0] + ".png")
                prev_coord = None

                self.keyPointsDict.append({})

                #read all coords, skipping over the 3rd coord (meta-coord).
                #If the index is even and isn't a multiple of 3, this is the
                #first coord for this point and we store it.
                #if it's odd, then this is the second coord and we may
                #add the point as a (prev_coord, this_coord) tuple.
                for idx, point_xy in enumerate(entries[3:]):
                    if (idx - 2) % 3 == 0: #the first index to ignore is 2, and then x+3 from there.
                        continue

                    if (idx - 1) % 3 == 0: #likewise, from index 1, every 3rd entry is the y coord.
                        self.keyPointsDict[-1][point_names[idx//3]] = (float(prev_coord), float(point_xy))
                        prev_coord = None

                    else:
                        prev_coord = point_xy

            lastIndices[f] = entry_idx
            ff.close()
        self.last_test_index = lastIndices[test_file]

    def get_original_image_path_relative_to_base_directory(self, i):
        if within_bounds(i, len(self.lstImages))
            return self.lstImages[i]
        return None

    def get_eyes_location(self, i):
        if within_bounds(i, len(self.keyPointsDict)):
            points = self.keyPointsDict[i]
            
            try:
                left = [x0 + (x1 - x0)/2 for x0, x1 in zip(points['right_eye_center_top'], points['right_eye_center_bottom'])]
                right = [x0 + (x1 - x0)/2 for x0, x1 in zip(points['left_eye_center_top'], points['left_eye_center_bottom'])]
                left.extend(right)
                return tuple(left)

            except KeyError:
                return None
        else:
            return None

    def get_keypoints_location(self, i):
        if within_bounds(i, len(self.keyPointsDict)):
            return self.keyPointsDict[i]

    def get_standard_train_test_splits(self):
        return (range(len(self.lstImages)-1, self.last_test_index, -1), 
                range(0, self.last_test_index + 1, 1)) #[0 .. self.last_test_index] inclusive.

    def __len__(self):
        return len(self.lstImages)
                

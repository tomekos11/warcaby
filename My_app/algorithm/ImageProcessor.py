import numpy as np
import cv2

class ImageProcessor:
    def __init__(self, model, image):
        self.pawn_dict= {
            'blue': 1,
            'red': 2,
            'blueK': 3,
            'redK': 4,
            'empty': 0,
            'bad': 'null'
        }
        self.ok_classes = [0, 1, 2, 3, 4]
        self.pawn_classes = [1, 2, 3, 4]
        self.bad_classes = [5]
        self.obstacles_classes = [6]

        self.model = model
        self.image = image
        self.image_np = np.array(self.image)

        self.results = self.predict()
        self.detected_objects = self.detect_objects()

        self.board_corners = self.find_board_corners()
        self.transformed_data = self.perspective_transform()
        self.board = [[0]*8 for _ in range(8)]

    def return_board_with_correct_index(self, ignore_bad=True):
        processed_board = []
        for row in self.board:
            processed_row = []
            for cell in row:
                if cell == 'bad' and ignore_bad:
                    processed_row.append(0)
                else:
                    processed_row.append(self.pawn_dict.get(cell, 0))
            processed_board.append(processed_row)
        return processed_board

    def draw_detected_objects_center(self, scale=1):
        if self.detected_objects:
            img_cp = self.image_np.copy()

            for obj in self.detected_objects:
                x = int(obj['bbox'][0])
                y = int(obj['bbox'][1])
                cv2.circle(img_cp, (x, y), radius=30, color=(255, 0, 0), thickness=-1)
            
            resized_image = cv2.resize(img_cp, (int(self.get_image_shape()[0] * scale), int(self.get_image_shape()[1] * scale)))
            cv2.imshow('Detected objects', resized_image)
            cv2.waitKey(0)

    def draw_corners(self, scale=1):
        if self.image and self.board_corners:
            img_cp = self.image_np.copy()

            for obj in self.board_corners:
                cv2.circle(img_cp, (obj[0], obj[1]), radius=30, color=(0, 0, 255), thickness=-1)
            
            resized_image = cv2.resize(img_cp, (int(self.get_image_shape()[0] * scale), int(self.get_image_shape()[1] * scale)))
            cv2.imshow('Corners', resized_image)
            cv2.waitKey(0)

    def draw_image_with_perspective_changed(self, scale=1):
        if self.board_corners:
            img_cp = self.transformed_data['image'].copy()

            for obj in self.transformed_data['objects']:
                x = int(obj['bbox'][0])
                y = int(obj['bbox'][1])
                w = int(obj['bbox'][2])
                h = int(obj['bbox'][3])

                cv2.circle(img_cp, (x, y), radius=30, color=(0, 0, 255), thickness=-1)
                #cv2.rectangle(img_cp, (int(x - w/2 * 0.85), int(y - h/2 * 0.85)), (int(x + w/2 * 0.85), int(y + h/2 * 0.85)), (0, 0, 255), 3)
            resized_image = cv2.resize(img_cp, (int(self.get_image_shape()[0] * scale), int(self.get_image_shape()[1] * scale)))
            cv2.imshow('Output', resized_image)
            cv2.waitKey(0)

    def draw_yolo_image(self):
        self.results.show()

    def predict(self):
        results = self.model(self.image)
        return results[0]
    
    def get_image_shape(self):
        return self.results[0].orig_shape

    def detect_objects(self):
        detected_objects = []

        for i, box in enumerate(self.results.boxes):
            cls = int(box.cls)
            class_name = self.model.names[cls]
            conf = float(box.conf)
            x1, y1, w, h = map(float, box.xywh[0])

            detected_objects.append({
                "class": class_name,
                "class_index" : cls,
                "confidence": conf,
                "bbox": (x1, y1, w, h)
            })
        return detected_objects
    
    def find_board_corners(self):
        if (sum(1 for obj in self.detected_objects if obj['class_index'] == 0) != 1 or
             any(obj['class_index'] in self.obstacles_classes for obj in self.detected_objects)):
            return []

        classes = self.results.boxes.cls.tolist()
        masks = self.results.masks

        points = []

        for i, tup in enumerate(zip(classes, masks)):
            if(classes[i] in self.ok_classes):
                _, mask = tup
                for point in mask.xy[0]:
                    x, y = int(point[0]), int(point[1])
                    points.append([x, y])

        points = np.array(points)
        hull = cv2.convexHull(points)
        hull_points = hull.reshape(-1, 2)

        min_x, max_x = np.min(hull_points[:, 0]), np.max(hull_points[:, 0])
        min_y, max_y = np.min(hull_points[:, 1]), np.max(hull_points[:, 1])

        half_x, half_y = (min_x + max_x) / 2, (min_y + max_y) / 2

        left_top_points = hull_points[(hull_points[:, 0] < half_x - 0.2 * half_x) & (hull_points[:, 1] < half_y - 0.2 * half_y)]
        right_top_points = hull_points[(hull_points[:, 0] > half_x + 0.2 * half_x) & (hull_points[:, 1] < half_y - 0.2 * half_y)]
        left_bottom_points = hull_points[(hull_points[:, 0] < half_x + 0.2 * half_x) & (hull_points[:, 1] > half_y + 0.2 * half_y)]
        right_bottom_points = hull_points[(hull_points[:, 0] > half_x + 0.2 * half_x) & (hull_points[:, 1] > half_y + 0.2 * half_y)]

        leftmost_top = (np.min(left_top_points[:, 0]), np.min(left_top_points[:, 1]))
        rightmost_top = (np.max(right_top_points[:, 0]), np.min(right_top_points[:, 1]))
        leftmost_bottom = (np.min(left_bottom_points[:, 0]), np.max(left_bottom_points[:, 1]))
        rightmost_bottom = (np.max(right_bottom_points[:, 0]), np.max(right_bottom_points[:, 1]))

        points = []
        for point in hull:
            distance_to_lt = np.sqrt((point[0][0] - leftmost_top[0]) ** 2 + (point[0][1] - leftmost_top[1]) ** 2)
            distance_to_rt = np.sqrt((point[0][0] - rightmost_top[0]) ** 2 + (point[0][1] - rightmost_top[1]) ** 2)
            distance_to_lb = np.sqrt((point[0][0] - leftmost_bottom[0]) ** 2 + (point[0][1] - leftmost_bottom[1]) ** 2)
            distance_to_rb = np.sqrt((point[0][0] - rightmost_bottom[0]) ** 2 + (point[0][1] - rightmost_bottom[1]) ** 2)

            points.append({
                "point": tuple(point),
                "distance_to_lt": distance_to_lt,
                "distance_to_rt": distance_to_rt,
                "distance_to_lb": distance_to_lb,
                "distance_to_rb": distance_to_rb
            })

        selected_points = [
            tuple(min(points, key=lambda p: p["distance_to_lt"])["point"][0]),
            tuple(min(points, key=lambda p: p["distance_to_rt"])["point"][0]),
            tuple(min(points, key=lambda p: p["distance_to_lb"])["point"][0]),
            tuple(min(points, key=lambda p: p["distance_to_rb"])["point"][0])
        ]

        return selected_points

    def perspective_transform(self):
        if len(self.board_corners) != 4:
            return {'image': None, 'objects': None}
        src_points = np.array(self.board_corners, dtype=np.float32)
        
        width = max(
            np.linalg.norm(src_points[1] - src_points[0]),
            np.linalg.norm(src_points[3] - src_points[2])
        )
        height = max(
            np.linalg.norm(src_points[2] - src_points[0]),
            np.linalg.norm(src_points[3] - src_points[1])
        )
        
        dst_points = np.array([
            [0, 0],
            [width - 1, 0],
            [0, height - 1],
            [width - 1, height - 1]
        ], dtype=np.float32)
        
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        
        image = self.image_np.copy()
        transformed_image = cv2.warpPerspective(image, matrix, (int(width), int(height)))
        
        transformed_objects = []
        
        for obj in self.detected_objects:
            x_center, y_center, w, h = obj['bbox']
            
            x_min = x_center - w / 2
            y_min = y_center - h / 2
            x_max = x_center + w / 2
            y_max = y_center + h / 2
            
            points = np.array([
                [x_min, y_min],
                [x_max, y_min],
                [x_min, y_max],
                [x_max, y_max]
            ], dtype=np.float32)
            
            points = np.array([points])
            transformed_points = cv2.perspectiveTransform(points, matrix)[0]
            
            x_coords = transformed_points[:, 0]
            y_coords = transformed_points[:, 1]
            new_x_min, new_y_min, new_x_max, new_y_max = x_coords.min(), y_coords.min(), x_coords.max(), y_coords.max()
            
            new_x_center = (new_x_min + new_x_max) / 2
            new_y_center = (new_y_min + new_y_max) / 2
            new_w = new_x_max - new_x_min
            new_h = new_y_max - new_y_min
            
            transformed_objects.append({
                'class': obj['class'],
                "class_index" : obj['class_index'],
                'confidence': obj['confidence'],
                'bbox': (new_x_center, new_y_center, new_w, new_h)
            })
        
        return {'image': transformed_image, 'objects': transformed_objects}
    
    def get_board(self):
        if  self.transformed_data['image'] is not None and self.transformed_data['objects'] != None:
            board = [[0]*8 for _ in range(8)]
            confidence_map = [[0] * 8 for _ in range(8)]
            bad_pawns = False

            image = self.transformed_data['image'].copy()
            
            sum_of_sizes = [0, 0, 0] #sumX, sumY, count
            for obj in self.transformed_data['objects']:
                class_index = obj['class_index']
                bbox = obj['bbox']
                confidence = obj['confidence']

                x = int(bbox[0] // (image.shape[1] / 8))
                y = int(bbox[1] // (image.shape[0] / 8))
                w = int(bbox[2])
                h = int(bbox[3])

                if 0 <= x < 8 and 0 <= y < 8:
                    if class_index in self.pawn_classes or class_index in self.bad_classes:
                        if confidence > confidence_map[y][x]:
                            board[y][x] = obj['class']
                            confidence_map[y][x] = confidence

                        if class_index in self.bad_classes:
                            bad_pawns = True

                        sum_of_sizes[0] += w * 0.75
                        sum_of_sizes[1] += h * 0.75
                        sum_of_sizes[2] += 1

            meanX = sum_of_sizes[0] / sum_of_sizes[2]
            meanY = sum_of_sizes[1] / sum_of_sizes[2]         
            self.board = board   
            if(meanY * 8 > image.shape[0] or meanX * 8 > image.shape[1]):
                return {'data' : [[0]*8 for _ in range(8)], 'status': 'error'}

            return {'data' : board, 'status': 'ok' if bad_pawns == False else 'bad_pawns'}
        else:
            return {'data' : [[0]*8 for _ in range(8)], 'status': 'error'}
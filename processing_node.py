import cv2
from mpi4py import MPI
import numpy as np
from PIL import Image
from utilities import Utilities
from numpy import asarray

class ProcessingNode:
    def __init__(self, **kwargs):
        self.comm = MPI.COMM_WORLD
        self.size = self.comm.Get_size()
        #self.size = 5
        self.rank = self.comm.Get_rank()
        self.params = kwargs

    def process_chunk(self, chunk, service_num, **kwargs):
        service_methods = {
            1: ('invert', {}),
            2: ('saturate', {'value': kwargs.get('value', 0)}),
            3: ('rgb_to_gray', {}),
            4: ('gray_to_rgb', {}),
            5: ('fourier_transform', {}),
            6: ('apply_lowpass_filter',
                {'cutoff_frequency': kwargs.get('cutoff_frequency', 1.0), 'order': kwargs.get('order', 1)}),
            7: ('apply_highpass_filter',
                {'cutoff_frequency': kwargs.get('cutoff_frequency', 1.0), 'order': kwargs.get('order', 1)}),
            8: ('blur_image', {'kernel_size': kwargs.get('kernel_size', 5)}),
            9: ('sharpen_image', {}),
            10: ('remove_gaussian_noise', {'kernel_size': kwargs.get('kernel_size', 3)}),
            11: ('remove_salt_pepper_noise', {'kernel_size': kwargs.get('kernel_size', 3)}),
            12: ('sobel_filter', {'kernel_size': kwargs.get('kernel_size', 3)}),
            13: ('prewitt_filter', {}),
            14: ('roberts_filter', {}),
            15: ('canny_edge_filter',
                 {'threshold1': kwargs.get('threshold1', 50), 'threshold2': kwargs.get('threshold2', 150)}),
            16: ('hough_transform', {'rho': kwargs.get('rho', 1), 'theta': kwargs.get('theta', np.pi / 180),
                                     'threshold': kwargs.get('threshold', 100)}),
            17: ('harris_corner_detection', {'blockSize': kwargs.get('blockSize', 2), 'ksize': kwargs.get('ksize', 3),
                                             'k': kwargs.get('k', 0.04)}),
            18: ('binary_threshold', {'threshold_value': kwargs.get('threshold_value', 128)}),
            19: ('otsu_threshold', {}),
            20: ('gaussian_adaptive_threshold',
                 {'block_size': kwargs.get('block_size', 2), 'constant': kwargs.get('constant', 0)})
        }

        if service_num in service_methods:
            method_name, params = service_methods[service_num]
            method = getattr(Utilities, method_name)
            processed_chunk = method(chunk, **params)
        else:
            raise ValueError(f"Service number {service_num} is not valid.")

        return processed_chunk

    def convert_image_to_array(self, image):
        img = Image.open('SB.jpg')
        img_pixels = asarray(img)
        print(type(img_pixels))
        #print(numpydata)
        print(img_pixels.shape)
        return img_pixels

    def reconstruct_array(self, result_array):
        min_val = np.min([np.min(chunk) for chunk in result_array if chunk is not None])
        max_val = np.max([np.max(chunk) for chunk in result_array if chunk is not None])
        result_array = [((chunk - min_val) * (255 / (max_val - min_val))).astype('uint8') for chunk in result_array if chunk is not None]
        result_array = np.concatenate(result_array)
        # Convert the array to an image
        if len(result_array.shape) == 2:
            image = Image.fromarray(result_array, 'L')
        else:
            image = Image.fromarray(result_array, 'RGB')
        return image

    # def send_to_request_handler(self, resulting_image):
    #     # Assuming RequestHandler has a method called receive_image
    #     request_handler = RequestHandler()
    #     request_handler.receive_image(resulting_image)

    def run(self, image, kernel_size=3, service_num=1):
        image_array = self.convert_image_to_array(image)
        chunk_size_row = image_array.shape[0] // (self.size-1)
        chunk_size_col = image_array.shape[1]
        num_channels = image_array.shape[2]
        chunk_size = (chunk_size_row, chunk_size_col, num_channels)
        overlap = kernel_size // 2
        print("overlap : ", overlap)
        if self.rank == 0:
            recv_chunks = []
            for i in range(1, self.size):
                # Determine the slice indices
                start_row = (chunk_size_row) * (i-1)
                end_row = ((chunk_size_row) * i)
                #print(f"Chunk size_{i}_BEFORE : ", start_row , " " , end_row)
                if i > 1:
                    start_row -= overlap
                    #print(f"{i} Entered IF 1")
                if i < self.size - 1:
                    #print(f"{i} Entered IF 2")
                    #print("MY RANK @ END", self.comm.rank)
                    end_row += overlap
                print("---------- i  : ", i, "start : ", start_row, "end :", end_row)
                # Extract chunk to be sent to worker
                chunk = image_array[start_row:end_row, :,:]
                print(f"Chunk size_{i}_AFTER : ", chunk.shape)
                # Save the chunk as an image
                cv2.imwrite(f"chunk_{i}.png", chunk)
                # Scatter chunk to workers
                self.comm.send(chunk, dest=i, tag=0)

            for i in range(1, self.size):
                # Gather processed chunks from workers
                processed_chunk = self.comm.recv(source=i, tag=0)
                recv_chunks.append(processed_chunk)
            # Reconstruct using the received chunks
            reconstructed_image = self.reconstruct_array(recv_chunks)
            return reconstructed_image
        else:
            if (self.comm.rank==1 or self.comm.rank==self.comm.size-1):
                print(f"MY RANK IF_1 {self.comm.rank}")
                #print("IDEAL SIZE : " ,chunk_size_row+1, chunk_size_col)
                chunk=np.zeros((chunk_size_row+1, chunk_size_col, num_channels), dtype=image_array.dtype)
            else:
                chunk = np.zeros((chunk_size_row+2, chunk_size_col, num_channels), dtype=image_array.dtype)
                print(f"MY RANK IF_2 {self.comm.rank}")
            print("CHUNKKK:" , chunk.shape)
            self.comm.recv(buf=chunk,source=0, tag=0)
            cv2.imwrite(f"recived_chunk_{self.comm.rank}.png",chunk)
            #chunk = image_array[start_row:end_row, :, :]
            processed_chunk = self.process_chunk(chunk, service_num, **self.params)
            # Save the chunk as an image
            cv2.imwrite(f"processed_chunk_{self.comm.rank}.png", processed_chunk)
            # Gather processed chunks on rank 0
            self.comm.send(processed_chunk, dest=0, tag=0)
if __name__ == "__main__":
    # Initialize the ProcessingNode with any required parameters
    node = ProcessingNode()

    # Define the path to your test image
    test_image_path = 'SB.jpg'
    image = cv2.imread(test_image_path)

    # Define the service number for the image processing task
    service_num = 1  # For example, '1' for invert operation

    # Run the processing node on the test image
    if node.rank == 0:
        # Only the coordinator process will handle the file input/output
        result_image = node.run(test_image_path, service_num=service_num)
        # Save or display the result image
        result_image.save('result_image.jpg')
    else:
        # Worker processes perform their part of the computation
        node.run(image, service_num=service_num)


import tempfile
import cv2
from mpi4py import MPI
import numpy as np
from PIL import Image
from utilities import Utilities
from numpy import asarray
import json
import Channel
import cloudCredentials
import os
class ProcessingNode:
    def __init__(self,**kwargs):
        self.comm = MPI.COMM_WORLD
        self.size = self.comm.Get_size()
        self.rank = self.comm.Get_rank()
        self.channel = None
        self.params = kwargs
        self.storage = cloudCredentials.Storage()

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
        print("Image type :" , type(image))
        print("---------------Entered Conversion-----------------")
        img_pixels = asarray(image)
        print("---------------Opened Image-----------------")
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

    def run(self,task_id,kernel_size=3, service_num=1):
        image= self.get_image(task_id)
        cv2.imwrite(f"image_to_be_processed.png",image)
        image_array = self.convert_image_to_array(image)
        #print ("Image_array",image_array)
        chunk_size_row = image_array.shape[0] // (self.size-1)
        chunk_size_col = image_array.shape[1]
        num_channels = image_array.shape[2]
        chunk_size = (chunk_size_row, chunk_size_col, num_channels)
        overlap = kernel_size // 2
        chunk = np.empty(chunk_size)
        print("overlap : ", overlap)
        if self.rank == 0:
            print ("Entered rank 0")
            recv_chunks = []
            for i in range(1, self.size):
                print ("Entered rank 0")
                # Determine the slice indices
                start_row = (chunk_size_row) * (i-1)
                end_row = ((chunk_size_row) * i)
                print(f"Chunk size_{i}_BEFORE : ", start_row , " " , end_row)
                if i > 1:
                    start_row -= overlap
                    print(f"{i} Entered IF 1")
                if i < self.size - 1:
                    print(f"{i} Entered IF 2")
                    print("MY RANK @ END", self.comm.rank)
                    end_row += overlap
                print("---------- i  : ", i, "start : ", start_row, "end :", end_row)
                # Extract chunk to be sent to worker
                chunk = image_array[start_row:end_row, :,:]
                print(f"Chunk size_{i}_AFTER : ", chunk.shape)
                # Save the chunk as an image
                cv2.imwrite(f"chunk_{i}.png", chunk)
                # Scatter chunk to workers
                req=self.comm.isend(chunk, dest=i, tag=0)
                req.wait()
                print(f"SEND ACK RECIEVED FROM {i}")

            for i in range(1, self.size):
                print (f"Entered rank {i} ")
                # Gather processed chunks from workers
                processed_chunk = self.comm.irecv(source=i, tag=0)
                processed_chunk.wait()
                print(f"RECV ACK RECIEVED FROM {i}")
                recv_chunks.append(processed_chunk)
            # Reconstruct using the received chunks
            reconstructed_image = self.reconstruct_array(recv_chunks)
            return reconstructed_image
        else:
            print("ENTERED ELSE FOR FIRST TIME-")
            # chunk = self.comm.recv(source=0, tag=0)
            req = self.comm.irecv(source=0, tag=0)
            req.wait()
            print(f"RECV ACK RECIEVED FROM 0")
            cv2.imwrite(f"recived_chunk_{self.comm.rank}.png",req)
            #chunk = image_array[start_row:end_row, :, :]
            processed_chunk = self.process_chunk(chunk, service_num, **self.params)
            # Save the chunk as an image
            cv2.imwrite(f"processed_chunk_{self.comm.rank}.png", processed_chunk)
            # Gather processed chunks on rank 0
            # self.comm.send(processed_chunk, dest=0, tag=0)
            req = self.comm.isend(processed_chunk, dest=0, tag=11)
            req.wait()
            print(f"SEND ACK RECIEVED FROM 0")
    def get_image (self,task_id):
        cv2.imwrite('IQ.jpg',self.storage.get_image(task_id))
        return self.storage.get_image(task_id)
    def callback(self, ch, method, properties, body):
        print(" [x] Processing Request %r" % body)
        request = json.loads(body)
        print("Request:",request)
        task_id = request['task_id']
        service_num = request['service_num']
        result_image = self.run(task_id=task_id,service_num=service_num)
        self.storage.upload_image(result_image, task_id)
        
    def listen_for_requests(self):
        try :
            self.channel.consume('requests', self.callback)
            print("Listening for requests")
        except Exception as e:
            print("Error while listening for requests")
            print(e)

    def open_channel_with_Rabbit(self):
        try :
            # Open a channel
            self.channel = Channel.Channel()
            print("Channel opened Successfully")
            self.listen_for_requests()
        except Exception as e:
            print("Channel not opened")
            print(e)
    
if __name__ == "__main__":
    # Initialize the ProcessingNode with any required parameters
    channel = Channel.Channel()
    node = ProcessingNode()
    node.open_channel_with_Rabbit()
    # Define the path to your test image
    # test_image_path = 'SB.jpg'
    # image = cv2.imread(test_image_path)

    # Define the service number for the image processing task
    service_num = 13  # For example, '1' for invert operation

    # # Run the processing node on the test image
    # if node.rank == 0:
    #     # Only the coordinator process will handle the file input/output
    #     result_image = node.run(test_image_path, service_num=service_num)
    #     # Save or display the result image
    #     result_image.save('result_image.jpg')
    # else:
    #     # Worker processes perform their part of the computation
    #     node.run(image, service_num=service_num)


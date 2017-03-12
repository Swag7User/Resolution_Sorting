import struct
import imghdr
import os

#Sort pictures in a directory based on their aspect ratio
#works for jpg, gif, png

#Thanks to some guy on stackexchange for this:
def get_image_size(fname):
    '''Determine the image type of fhandle and return its size.
    from draco'''
    with open(fname, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return
        if imghdr.what(fname) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif imghdr.what(fname) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imghdr.what(fname) == 'jpeg':
            try:
                fhandle.seek(0) # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception: #IGNORE:W0703
                return
        else:
            return
        return width, height
		
directory = r'C:\...\D' #source directory
directoryNewV = r'C:\...\V' # vertical pictures destination
directoryNewH = r'C:\...\H' # horizontal pictures destination
for filename in os.listdir(directory):
	if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png") or filename.endswith(".gif"): 
		# print(os.path.join(directory, filename))
		tuple = get_image_size(os.path.join(directory, filename))
		if tuple is None:
			continue
		if tuple[0] / tuple[1] > 1.19: # Horizontal ratio, tweak if necessary
			os.rename(os.path.join(directory, filename), os.path.join(directoryNewH, filename))
		if tuple[0] / tuple[1] < 0.81: # Vertical ratio, tweak if necessary
			os.rename(os.path.join(directory, filename), os.path.join(directoryNewV, filename))
			#With this method there will be some pictires left unsorted, this is on purpose in order to decide on a case by case basis, if this is not wanted tewak the ratio to eliminate any left overs
		continue
	else:
		continue
from __future__ import division
import struct
import imghdr
import shutil
import time
import sys, traceback
import os

#Sort pictures in a directory based on their aspect ratio
#works for jpg, gif, png

srcDirectory = r'C:\source' #source directory
directoryNewV = r'C:\vertical' # vertical pictures destination
directoryNewH = r'C:\horizontal' # horizontal pictures destination
Hratio = 1.01 # Horizontal ratio, tweak if necessary
Vratio = 0.99 # Vertical ratio, tweak if necessary
prefixFilter = 'zz' # only sort images that are in a directory with this prefix



# Thanks to some guy on stackexchange for this:
def get_image_size(fnameS):
    '''Determine the image type of fhandle and return its size.
    from draco'''
    fname = '\\\\?\\' + fnameS # extended path compliance
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


# prepare some stuff

ts = time.gmtime()
logfile2name = time.strftime("%Y-%m-%d_%H-%M-%S", ts)
logfile2name += '_logfile2.rslog'
with open(logfile2name, 'w') as logfile2:
    logfile2.write('Started copy run on: ' + time.strftime("%Y-%m-%d %H:%M:%S", ts) +'\n')
    logfile2.write('Baseparameter: ' +'\n')
    logfile2.write(' - ' +  'logfile2name: ' + logfile2name +'\n')
    logfile2.write(' - ' +  'Source Directory: ' + srcDirectory +'\n')
    logfile2.write(' - ' +  'Vertical image Directory: ' + directoryNewV +'\n')
    logfile2.write(' - ' +  'Horizontal image Directory: ' + directoryNewH +'\n')
    logfile2.write(' - ' +  'Horizontal Ratio: ' + str(Hratio) +'\n')
    logfile2.write(' - ' +  'Vertical Ratio: ' + str(Vratio) +'\n')
    logfile2.write(' - ' +  'Prefix Filter: ' + prefixFilter +'\n')

    fileinfo = 'no fileinfo yet'
    if not os.path.exists(directoryNewV):
        os.makedirs(directoryNewV)
        logfile2.write('created vertical target directory: ' + directoryNewV +'\n')
    if not os.path.exists(directoryNewH):
        os.makedirs(directoryNewH)
        logfile2.write('created horizontal target directory: ' + directoryNewV +'\n')
    logfile2.write('--------------------------------------------------------' +'\n')
    logfile2.write('\n')
    logfile2.write('\n')



    # start sorting and copying
    for directory, dirs, files in os.walk(srcDirectory):     
            path = directory.split('/')
            print '|', (len(path))*'---', '[',os.path.basename(directory),']'
            logmessage = '|'+ (len(path))*'---'+ '['+os.path.basename(directory)+']'+'\n'
            logfile2.write(logmessage)
            for filename in files:
                if os.path.basename(directory).startswith(prefixFilter):
                    if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png") or filename.endswith(".gif"): 
                            tuple = get_image_size(os.path.join(directory, filename))
                            try:
                                if tuple is None:
                                        continue
                                elif tuple[0] / tuple[1] > Hratio:
                                        shutil.copy2(os.path.join('\\\\?\\' + directory, filename), os.path.join(directoryNewH, filename))
                                        logfile2.write(str(tuple[0]) + ' / ' + str(tuple[1]) + ' = ' + str(tuple[0] / tuple[1])+ '\n')
                                        logfile2.write(str('H - '+ os.path.join(directory, filename)+ '  --->  ' + os.path.join(directoryNewH, filename)+ '\n') )                           
                                elif tuple[0] / tuple[1] < Vratio:
                                        shutil.copy2(os.path.join('\\\\?\\' + directory, filename), os.path.join(directoryNewV, filename))
                                        logfile2.write(str(tuple[0]) + ' / ' + str(tuple[1]) + ' = ' + str(tuple[0] / tuple[1])+ '\n')
                                        logfile2.write(str('V - '+ os.path.join(directory, filename)+ '  --->  ' + os.path.join(directoryNewV, filename)+ '\n') )
                                elif tuple[0] / tuple[1] <= Hratio and tuple[0] / tuple[1] >= Vratio: # everything that is nearly square will be handled here. (here it is sorted to the vertical dir)
                                        shutil.copy2(os.path.join('\\\\?\\' + directory, filename), os.path.join(directoryNewV, filename))
                                        logfile2.write(str(tuple[0]) + ' / ' + str(tuple[1]) + ' = ' + str(tuple[0] / tuple[1])+ '\n')
                                        logfile2.write(str('VS - '+ os.path.join(directory, filename)+ '  --->  ' + os.path.join(directoryNewV, filename)+ '\n') )
                                else:
                                        logfile2.write('This should not happen')
                            except TypeError:
                                print sys.exc_info()
                            except:
                                print os.path.join(directory, filename)
                                print 'directory length: ' + str(len(directory))
                                print 'filename length: ' + str(len(filename))
                                print 'absolute path length: ' + str(len(os.path.join(directory, filename)))
                                print get_image_size(os.path.join(directory, filename))
                                print sys.exc_info()
                                print '-'*60
                                traceback.print_exc(file=sys.stdout)
                                print '-'*60
                            continue
                    else:
                             continue
                else:
                    continue
logfile2.closed

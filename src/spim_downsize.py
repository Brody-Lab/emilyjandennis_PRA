#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 12:04:02 2020

@author: wanglab
"""

import os, cv2, shutil, sys, imageio
import numpy as np
import tifffile as tif
import multiprocessing as mp
from scipy.ndimage import zoom

def fast_scandir(dirname):
    """ gets all folders recursively """
    subfolders= [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders

def resize_helper(img, dst, resizef):
    print(os.path.basename(img))
    im = imageio.volread(img)
    y,x = im.shape
    yr = int(y/resizef); xr = int(x/resizef)
    im = cv2.resize(im, (xr, yr), interpolation=cv2.INTER_AREA)
    tif.imsave(os.path.join(dst, os.path.basename(img)),
                    im.astype("uint16"), compress=1)
def get_folderstructure(dirname):
    folderstructure = []
    for i in os.walk(src):
        folderstructure.append(i)
    return folderstructure

def dwnsz(pth,save_str,src):
    savestr=save_str
    print("\nPath to stitched images: %s\n" % pth)
    #path to store downsized images
    dst = os.path.join(os.path.dirname(src), "{}_downsized".format(save_str))
    print("\nPath to storage directory: %s\n\n" % dst)
    if not os.path.exists(dst): os.mkdir(dst)
    imgs = [os.path.join(pth, xx) for xx in os.listdir(pth) if "tif" in xx]
    z = len(imgs)
    resizef = 5 #factor to downsize imgs by
    print("resizing {} images by {} times".format(z,resizef))
    iterlst = [(img, dst, resizef) for img in imgs]
    p = mp.Pool(12)
    p.starmap(resize_helper, iterlst)
    p.terminate()

    #now downsample to 140% of pra atlas
    imgs = [os.path.join(dst, xx) for xx in os.listdir(dst) if "tif" in xx]; imgs.sort()
    z = len(imgs)
    y,x = imageio.volread(imgs[0]).shape
    arr = np.zeros((z,y,x))
    atlpth = "/scratch/ejdennis/mPRA_0703.tif"
    atl = imageio.volread(atlpth)
    atlz,atly,atlx = atl.shape #get shape, sagittal
    print("############### THE ATLAS AXES ARE {},{},{}".format(atlz,atly,atlx))    
    #read all the downsized images
    for i,img in enumerate(imgs):
        if i%5000==0: print(i)
        arr[i,:,:] = imageio.volread(img) #horizontal
    zz,yy,xx=arr.shape
    print("############### THE AXES ARE {},{},{}".format(zz,yy,xx))
    #switch to sagittal
    arrsag = np.swapaxes(arr,2,0)
    z,y,x = arrsag.shape
    print("############### THE NEW AXES ARE {},{},{}".format(z,y,x))
    print("\n**********downsizing....heavy!**********\n")
    #arrsagd = cv2.resize(arrsag, (round(atlz*1.4),round(atly*1.4),round(atlx*1.4)), interpolation=cv2.INTER_AREA) # memory issues
    arrsagd = zoom(arrsag,((atlz*1.4/z),(atly*1.4/y),(atlx*1.4/x)),order=1)

    # conservatively chop outliers to maximize dynamic range
    lims = np.percentile(arrsagd,(0.001,99.999))    
    arrsagd[arrsagd>lims[1]] = lims[1]
    arrsagd[arrsagd<lims[0]] = lims[0]

    print('saving tiff at {}'.format(os.path.join(os.path.dirname(dst), "{}_downsized_for_atlas.tif".format(savestr))))
    tif.imsave(os.path.join(os.path.dirname(dst), "{}_downsized_for_atlas.tif".format(savestr)), arrsagd.astype("uint16"))


if __name__ == "__main__":

    #takes 3 command line args
    print(sys.argv)
    src=str(sys.argv[1]) #folder to main image folder
    rawdata=[]
    rawdata.append(os.path.join(src,str(sys.argv[2])))
    rawdata.append(os.path.join(src,str(sys.argv[3])))
    print(rawdata)

    for i in rawdata:
        if 'Ex_488' in i:
            reg_ch = i
            while len([file for file in os.listdir(reg_ch) if '.tif' in file]) < 10:
                reg_ch = os.path.join(reg_ch,[f.name for f in os.scandir(reg_ch) if f.is_dir()][0])
            print('reg ch is {}'.format(reg_ch))
            dwnsz(reg_ch,'reg_',src)
        else :
            cell_ch=i
            while len([file for file in os.listdir(cell_ch) if '.tif' in file]) < 10:
       	       	cell_ch = os.path.join(cell_ch,[f.name for f in os.scandir(cell_ch) if f.is_dir()][0])
            print('cell ch is {}'.format(cell_ch))
            dwnsz(cell_ch,'cell_',src)
    print('done')

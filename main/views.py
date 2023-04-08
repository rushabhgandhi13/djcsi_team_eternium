import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from django.shortcuts import render, redirect
from .models import Imag
from mmseg.apis import inference_model, init_model, show_result_pyplot

# Create your views here.

# model initiation
config_file = "main/static/mmsegmentation/configs/pspnet/pspnet_r101-d8_4xb4-80k_pascal-context-59-480x480.py"
ckpt_path = "main/static/checkpoints/pspnet_r101-d8_480x480_80k_pascal_context_59_20210416_114418-fa6caaa2.pth"
model = init_model(config=config_file, checkpoint=ckpt_path, device="cpu")

# PASCAL Context 
CLASSES = ['background', 'aeroplane', 'bag', 'bed', 'bedclothes', 'bench',
               'bicycle', 'bird', 'boat', 'book', 'bottle', 'building', 'bus',
               'cabinet', 'car', 'cat', 'ceiling', 'chair', 'cloth',
               'computer', 'cow', 'cup', 'curtain', 'dog', 'door', 'fence',
               'floor', 'flower', 'food', 'grass', 'ground', 'horse',
               'keyboard', 'light', 'motorbike', 'mountain', 'mouse', 'person',
               'plate', 'platform', 'pottedplant', 'road', 'rock', 'sheep',
               'shelves', 'sidewalk', 'sign', 'sky', 'snow', 'sofa', 'table',
               'track', 'train', 'tree', 'truck', 'tvmonitor', 'wall', 'water',
               'window', 'wood']
wall_indx = CLASSES.index("wall") - 1

def home(request):
    if request.method=="POST":
        img=Imag()
        img.image=request.FILES.get('roomimage')
        img.save()
        return redirect('decor', pk=img.img_id)
    return render(request, 'main/home.html')

def decor(request, pk):
    img=Imag.objects.get(img_id=pk)
    # print(img.image)
    # print(img.image.url)
    return render(request, 'main/decor.html', {'img': img})


def segment(request, pk):
    img=Imag.objects.get(img_id=pk)
    img_rel_path = img.image.url    
    img_abs_path = f".{img_rel_path}"
    
    result = inference_model(model, img_abs_path)
    mask = result.pred_sem_seg.data
    
    img = plt.imread(img_abs_path)
    mask = np.squeeze(mask, axis=0).numpy()
    
    mask_55 = np.zeros_like(mask)
    mask_55[mask == 55] = 1
    
    # Create a new figure
    fig, ax = plt.subplots()

    # Plot the image
    ax.imshow(img)

    # wall color
    color = (255, 0, 255)
    colors = [(0, 0, 0), color]
    cmap = mcolors.ListedColormap(colors)

    # Plot the mask on top of the image
    masked_image = cmap(mask_55)
    masked_image = masked_image[:,:,:3]
    ax.imshow(masked_image, alpha=0.5)
    ax.set_axis_off()
        
    fname = os.path.basename(img_abs_path)
    fname = fname[:-4] + f"_{color}.jpg"
    fname = os.path.join("images", "results", fname)
    plt.savefig(fname)
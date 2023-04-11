import os
import cv2
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from django.shortcuts import render, redirect
from PIL import Image, ImageDraw
from django.contrib.staticfiles.storage import staticfiles_storage
from .models import Imag, Point, SegmentedImages, Suggestions
from mmseg.apis import inference_model, init_model, show_result_pyplot
from segment_anything import sam_model_registry, SamPredictor, SamAutomaticMaskGenerator

# Create your views here.

# model initiation

## pspnet
# config_file = "main/static/mmsegmentation/configs/pspnet/pspnet_r101-d8_4xb4-80k_pascal-context-59-480x480.py"
# ckpt_path = "main/static/checkpoints/pspnet_r101-d8_480x480_80k_pascal_context_59_20210416_114418-fa6caaa2.pth"
# model = init_model(config=config_file, checkpoint=ckpt_path, device="cpu")


## sam
print("Loading SAM model...")
sam_checkpoint = "main/static/checkpoints/sam_vit_l_0b3195.pth"
model_type = "vit_l"
device = "cpu"
sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)
predictor = SamPredictor(sam)
print("Loaded SAM")

COLOR_THEMES = [
["eec9d2", "f4b6c2", "f6abb6"],
["011f4b", "005b96", "b3cde0"],
["3da4ab", "f6cd61", "fe8a71"],
["adcbe3", "e7eff6", "63ace5"],
["fec8c1", "fad9c1", "f9caa7"],
["009688", "35a79c", "54b2a9"],
["fdf498", "7bc043", "0392cf"],
["ee4035", "f37736", "fdf498"],
["ffffff", "d0e1f9", "4d648d"],
["eeeeee", "dddddd", "cccccc"],
["ff6f69", "ffcc5c", "88d8b0"],
["008744", "0057e7", "ffa700"]
]


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
        sPoints = request.POST.get('coords').split('|')
        coords = [[int(j) for j in i.split(',')] for i in sPoints if len(i) != 0]
        print(coords)
        for i in coords:
            point=Point()
            point.img_id=img
            point.x=i[0]
            point.y=i[1]
            point.save()
        return redirect('segment', pk=img.img_id)
    return render(request, 'main/home.html')

def decor(request, pk):
    img=Imag.objects.get(img_id=pk)
    if request.method == "POST":
        color=str(request.POST.get('color'))
        final=[]
        for i in (0, 2, 4):
            decimal = int(color[i+1:i+3], 16)
            final.append(decimal)
        return redirect('decor', pk=pk)
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


def sam_segment(request, pk):
    points = Point.objects.filter(img_id = pk)
    img=Imag.objects.get(img_id=pk)
    img_rel_path = img.image.url    
    img_abs_path = f".{img_rel_path}"
    mask_55 = []
    previous_mask = np.array([])
    check = False
    color_check = False
    if SegmentedImages.objects.filter(segImg_id = img).exists():
        check = True
    else:
        check = False

    if request.method == "POST":
        if request.POST.get('colorchecker') == "on":
            colors = request.POST.getlist('color')
            for i in range(0,len(points)):
                points[i].color = colors[i]
                points[i].save()
        else:
            colors=request.POST.getlist('col1')
            for i in range(0,len(points)):
                temp_color=colors[i].split(',')
                colors[i]=(int(temp_color[0]),int(temp_color[1]),int(temp_color[2]))
                points[i].color = '#%02x%02x%02x' % colors[i]
                points[i].save()
            print(colors)
        previous_mask = (SegmentedImages.objects.get(segImg_id = img))
        # print(np.frombuffer(previous_mask.segmentedImageMask, dtype=np.uint8))
        previous_mask = np.frombuffer(previous_mask.segmentedImageMask.encode('ISO-8859-1'), dtype=np.uint8)
        SegmentedImages.objects.get(segImg_id = img).delete()
        check = False
        color_check = True


    colorMap = Point.objects.filter(img_id = pk).values_list('color', flat=True)

    if check:
        pass
    else:
        image = cv2.imread(img_abs_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        print("Transforming image")
        predictor.set_image(image)
        print("Transforming image done")
        # if previous_mask.size == 0:
        #     print("Transforming image")
        #     predictor.set_image(image)
        #     print("Transforming image done")
        
        w, h = image.shape[0], image.shape[1]
        print(image.shape[0])
        print([[i.x, i.y] for i in points])
        p = [[(h/700) * i.x, (w/700) *i.y] for i in points]
        print(p)
        # Create a new figure
        fig, ax = plt.subplots()

        # Plot the image    
        # ax.imshow(image)
        pil_image = Image.fromarray(image)
        for point, j in zip(p, points):
            input_point = np.array([point])
            input_label = np.array([1])
            
            print("Predicting...")

            # if previous_mask.size != 0:
            #     mask = previous_mask
            # else:
            #     mask, scores, logits = predictor.predict(
            #         point_coords=input_point,
            #         point_labels=input_label,
            #         multimask_output=False,
            #     )
            mask, scores, logits = predictor.predict(
                point_coords=input_point,
                point_labels=input_label,
                multimask_output=False,
            )
            # print(f"mask length: {len(str(mask))}")
            mask = np.squeeze(mask, axis=0)
            
            mask_55 = np.zeros_like(mask)

            
            # create a gray scale image from an rgb image
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # print(image_gray.shape)
            

            mask_55[mask == True] = 128
            # print(mask_55)
            # print(mask_55.shape)
            # print(mask_55[0])
            # print(mask_55[0][0])
            # for i in range(0, mask.shape[0]):
            #     for k in range(0, mask.shape[1]):
            #         mask_55[i][k] = 175/image_gray[i][k] * 255

            if not color_check:
            # wall color
                red = random.randint(0, 255)
                green = random.randint(0, 255)
                blue = random.randint(0, 255)
                color = (red, green, blue)
                
                j.color = '#%02x%02x%02x' % color
                j.save()
            else:
                color = j.color
                color = color[1:]
                color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                print(color)
            colors = [(0, 0, 0), color]
            cmap = mcolors.ListedColormap(colors)

            # Plot the mask on top of the image
            masked_image = cmap(mask_55)
            masked_image = masked_image[:,:,:3]
            
            draw = ImageDraw.Draw(pil_image)
            mask_pil = Image.fromarray(mask_55)
            # print(mask_pil[0])
            # print(mask_pil[0][0])
            draw.bitmap((0, 0), mask_pil, fill=color)
            
            # ax.imshow(masked_image, alpha=0.5)
            # ax.set_axis_off()

        # Show the image

        fname = os.path.basename(img_abs_path)
        fname = fname.split('.')[0] + f"_{color}.{fname.split('.')[1]}"
        fname = os.path.join("images", "results", fname)
        print(fname)

        segImg = SegmentedImages()
        segImg.segImg_id = img
        segImg.segmentedImage = fname
        segImg.segmentedImageMask = mask.tobytes().decode('ISO-8859-1')
        segImg.save()
        pil_image.save(fname)

    segImg = SegmentedImages.objects.get(segImg_id = img.img_id)
    
    # plt.savefig(fname)

    return render(request, 'main/decor.html', {'img': img, 'segImg': segImg, 'colorMap': colorMap, 'pk': pk})

def suggestions(request, pk):
    img=Imag.objects.get(img_id=pk)
    path=Imag.objects.all()
    points = Point.objects.filter(img_id = pk)
    
    if Suggestions.objects.filter(sugImg_id = img).exists():
        check = True
    else:
        img_rel_path = img.image.url    
        img_abs_path = f".{img_rel_path}"
        
        print("Transforming image")
        image = cv2.imread(img_abs_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        predictor.set_image(image)
        print("Transforming image done")
        
        w, h = image.shape[0], image.shape[1]
        print(image.shape[0])
        print([[i.x, i.y] for i in points])
        p = [[(h/700) * i.x, (w/700) *i.y] for i in points]
        print(p)

        for theme in COLOR_THEMES: 
            print(theme)
            pil_image = Image.fromarray(image)
            count = 0 
            for point, j in zip(p, points):
                input_point = np.array([point])
                input_label = np.array([1])
                
                print("Predicting...")
                mask, scores, logits = predictor.predict(
                    point_coords=input_point,
                    point_labels=input_label,
                    multimask_output=False,
                )
                mask = np.squeeze(mask, axis=0)
                
                mask_55 = np.zeros_like(mask)
                mask_55[mask == True] = 255

                color = tuple(int(theme[count][i:i+2], 16) for i in (0, 2, 4))
                count += 1
                
                colors = [(0, 0, 0), color]
                cmap = mcolors.ListedColormap(colors)

                # Plot the mask on top of the image
                masked_image = cmap(mask_55)
                masked_image = masked_image[:,:,:3]
                
                draw = ImageDraw.Draw(pil_image)
                mask_pil = Image.fromarray(mask_55)
                draw.bitmap((0, 0), mask_pil, fill=color)


            # Show the image
            fname = os.path.basename(img_abs_path)
            fname = fname.split('.')[0] + f"_{color}.{fname.split('.')[1]}"
            fname = os.path.join("images", "suggestions", fname)
            print(fname)
            pil_image.save(fname)
            
            s_img = Suggestions(sugImg_id=img, sugImage=fname)
            s_img.save()

        # for texture
        url = "main/" + staticfiles_storage.url('textures')
        textures = os.listdir(url)
        
        for i, texture in enumerate(textures):
            point = random.choice(p)
            print(point)
            input_point = np.array([point])
            input_label = np.array([1])
            pil_image = Image.fromarray(image)
            texture_path = os.path.join(url, texture)
            texture_img = Image.open(texture_path)
            texture_img = texture_img.resize(pil_image.size)
            
            mask, scores, logits = predictor.predict(
                point_coords=input_point,
                point_labels=input_label,
                multimask_output=False,
            )
            mask = np.squeeze(mask, axis=0)
            
            mask_55 = np.zeros_like(mask)
            mask_55[mask == True] = 255
            
            masked_image = masked_image[:,:,:3]
            mask_pil = Image.fromarray(mask_55)
            
            pil_image = Image.composite(texture_img, pil_image, mask_pil)   
            
            # Show the image
            fname = os.path.basename(img_abs_path)
            fname = fname.split('.')[0] + f"_texture_{i}.{fname.split('.')[1]}"
            fname = os.path.join("images", "suggestions", fname)
            print(fname)
            pil_image.save(fname)
            
            s_img = Suggestions(sugImg_id=img, sugImage=fname)
            s_img.save()

    paths = Suggestions.objects.filter(sugImg_id=pk)
    return render(request, 'main/suggestions.html', {'pk': pk, 'img': img, 'paths': paths})

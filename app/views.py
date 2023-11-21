from django.shortcuts import render, redirect
from django.conf import settings
from .models import File,Comment
from django.contrib import messages
from django.utils import timezone
from .utils import convert_pdf_to_img,convert_pdf_to_img_all
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from .forms import FileForm, CommentForm     
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
app_name = 'app' 

def file_list(request):
    search_query = request.GET.get('search', '')
    sort = request.GET.get('sort', 'latest')

    # 검색 조건에 따라 파일을 필터링합니다.
    if search_query:
        files_list = File.objects.filter(
            Q(subject__icontains=search_query) | Q(author__username__icontains=search_query)
        )
    else:
        files_list = File.objects.all()

    # 정렬 조건을 적용합니다.
    if sort == 'likes':
        files_list = files_list.order_by('-likes')
    else:  # 기본 정렬은 'latest'로, 생성 날짜 기준으로 내림차순 정렬합니다.
        files_list = files_list.order_by('-create_date')

    paginator = Paginator(files_list, 5)  # 페이지당 5개의 파일을 보여주도록 설정합니다.
    page = request.GET.get('page')  # URL에서 페이지 번호를 가져옵니다.

    try:
        files = paginator.page(page)
    except PageNotAnInteger:
        files = paginator.page(1)
    except EmptyPage:
        files = paginator.page(paginator.num_pages)

    files_with_images = []
    for file in files:
        image_url = settings.MEDIA_URL + convert_pdf_to_img(file.file) if convert_pdf_to_img(file.file) else None
        files_with_images.append({
            'file': file,
            'image_url': image_url
        })

    return render(request, 'app/main.html', {
        'files_with_images': files_with_images,
        'page_obj': files  # 페이징 객체 추가
    })


def detail(request, item_id):
    file = File.objects.get(id=item_id)
    comments = file.comment_set.all().order_by('-creation_date')
    image_url_all = []
    image_path = convert_pdf_to_img_all(file.file)
    comment_form = CommentForm()
    if image_path:
        for i in image_path:
            image_url = settings.MEDIA_URL + i  # 웹 URL로 사용될 경로
            image_url_all.append(image_url)
        file_info = {
            'file': file,
            'image_url': image_url_all,  
        }
    else:
        file_info = {
            'file': file,
            'image_url': [],  # 이미지 변환이 실패하면 None
        }
    return render(request, 'app/file_detail.html', {'file_info': file_info, 'comment_form': comment_form,  'comments': comments})

# views.py


def create_file(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)  # 파일 업로드를 처리하기 위해 request.FILES 추가
        if form.is_valid():
            new_file = form.save(commit=False)  # form의 데이터로 File 모델 인스턴스를 생성하지만, 아직 데이터베이스에 저장하지 않음
            new_file.author = request.user  # 파일의 작성자를 현재 로그인한 사용자로 설정
            new_file.create_date = timezone.now()
            
            new_file.save()  # 데이터베이스에 저장
            return redirect('app:file_list')  # 파일 목록 페이지로 리다이렉트
    else:
        form = FileForm()  # GET 요청 시 빈 폼을 생성

    return render(request, 'app/create_file.html', {'form': form})
@login_required
@csrf_exempt
def like_file(request, item_id):
    file = File.objects.get(id=item_id)
    if request.user in file.voter.all():
        file.likes -= 1
        file.voter.remove(request.user)
        liked = False
    else:
        file.likes += 1
        file.voter.add(request.user)
        liked = True
    file.save()
    return JsonResponse({'likes': file.likes, 'liked': liked})


def comment_create(request, file_id):
    file = get_object_or_404(File, pk=file_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user  # 유저 이름으로 저장
            comment.creation_date = timezone.now()

            comment.file = file
            comment.save()
            return redirect('app:detail', item_id=file_id)
        else:
            # 폼 유효성 검사에 실패했을 때 오류를 포함하여 같은 페이지를 다시 렌더링
            file = File.objects.get(id=file_id)
            comments = file.comment_set.all().order_by('-creation_date')
            image_url_all = []
            image_path = convert_pdf_to_img_all(file.file)
            comment_form = CommentForm()
            if image_path:
                for i in image_path:
                    image_url = settings.MEDIA_URL + i  # 웹 URL로 사용될 경로
                    image_url_all.append(image_url)
                file_info = {
                    'file': file,
                    'image_url': image_url_all,  
                }
            else:
                file_info = {
                    'file': file,
                    'image_url': [],  # 이미지 변환이 실패하면 None
                }
            context = {'file_info': file_info, 'comment_form': comment_form,  'comments': comments , 'form':form}
            return render(request, 'app/file_detail.html', context)
    else:
        form = CommentForm()
    context = {'file': file, 'form': form}
    return redirect('app:detail', item_id=file_id)


@login_required(login_url='common:login')
def file_modify(request, item_id):
    file = get_object_or_404(File, pk=item_id)
    if request.user != file.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('app:detail', item_id=file.id)
    if request.method == "POST":
        form = FileForm(request.POST, instance=file)
        if form.is_valid():
            file = form.save(commit=False)
            file.modify_date = timezone.now()  # 수정일시 저장
            file.save()
            return redirect('app:detail', item_id=file.id)
    else:
        form = FileForm(instance=file)
    context = {'form': form}
    return render(request, 'app/question_form.html', context)

@login_required(login_url='common:login')
def file_delete(request, item_id):
    file = get_object_or_404(File, pk=item_id)
    if request.user != file.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('app:detail', item_id=file.id)
    file.delete()
    return redirect('app:file_list')

@login_required(login_url='common:login')
def comment_modify(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('app:detail', item_id=comment.file.id)
    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.modify_date = timezone.now()
            comment.save()
            return redirect('app:detail', item_id=comment.file.id)
    else:
        form = CommentForm(instance=comment)
    context = {'answer': comment, 'form': form}
    return render(request, 'app/answer_form.html', context)

@login_required(login_url='common:login')
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '삭제권한이 없습니다')
    else:
        comment.delete()
    return redirect('app:detail', item_id=comment.file.id)


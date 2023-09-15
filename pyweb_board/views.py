import os
import urllib

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from pyweb_board.models import Board, Comment
from django.http.response import HttpResponse

# Create your views here.
upload_dir = 'pyweb_board/static/upload/'


def list(request):
    boardCount = Board.objects.count()
    boardList = Board.objects.all().order_by("-idx")
    return render(request, "board/list.html",
                  {"boardList": boardList, "boardCount": boardCount})


# render(request, 렌더링할 페이지 json)
# -idx : 내림 <-> idx

def write(request):
    return render(request, 'board/write.html')


@csrf_exempt  # 보안토큰
def insert(request):
    fname = ''
    fsize = 0

    # 파일 업로드
    if 'file' in request.FILES:
        # write.html에 name='file'이 있는지 확인
        file = request.FILES['file']
        fname = file.name
        fsize = file.size

        # 파일 업로드하는 디렉토리 필요 : 맨 위에 생성
        fp = open("%s%s" % (upload_dir, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()
        # wb : write binary
        # chunk : 파일에서 기록되는 단위 블록

    # POST로 전달된 것 중 writer/title/content를 변수에 저장
    w = request.POST['writer']
    t = request.POST['title']
    c = request.POST['content']

    # 객체로 저장해 리턴
    dto = Board(writer=w, title=t, content=c, filename=fname, filesize=fsize)
    dto.save()

    # redirect는 render를 import한 것에서 추가만
    return redirect('/list/')


# 첨부파일 다운로드
def download(request):
    id = request.GET['idx']  # list.html -> 파일 다운로드 할 때, 게시판 idx 가져옴
    dto = Board.objects.get(idx=id)
    path = upload_dir + dto.filename
    filename = os.path.basename(path)
    # file_name = urllib.parse.quote(filename) 한글인데 안됨..

    with open(path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet=stream')
        response['Content-Disposition'] = "attachment;filename*=UTF-8''{0}".format(filename)

    dto.down_up()
    dto.save()
    return response


def detail(request):
    id = request.GET['idx']
    dto = Board.objects.get(idx=id)  # get 데이터 하나 가져오기
    dto.hit_up()  # 조회 수 증가
    dto.save()

    # 해당 게시물에 딸린 댓글이 필요
    commentList = Comment.objects.filter(board_idx=id).order_by("idx")  # 최근 댓글 맨 위
    filesize = "%.2f" % (dto.filesize)

    return render(request, "board/detail.html",
                  {'dto': dto, 'filesize': filesize, 'commentList': commentList})


# POST는 csfr_exempt가 필요
@csrf_exempt
def update(request):
    id = request.POST['idx']
    dto_src = Board.objects.get(idx=id)
    fname = dto_src.filename
    fsize = dto_src.filesize

    w = request.POST['writer']
    t = request.POST['title']
    c = request.POST['content']

    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fp = open('%s%s' % (upload_dir, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()
        fsize = os.path.getsize(upload_dir + fname)

    dto_new = Board(idx = id, writer = w, title = t, content = c, filename = fname, filesize = fsize)
    dto_new.save()

    return redirect("/list/")

@csrf_exempt
def delete(request):
    id = request.POST['idx']
    Board.objects.get(idx=id).delete()
    return redirect("/list/")

@csrf_exempt
def reply_insert(request):
    id = request.POST['idx']
    dto = Comment(board_idx = id, writer = request.POST['writer'],content= request.POST['content'])
    dto.save()
    return HttpResponseRedirect("/detail?idx="+id)

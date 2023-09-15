import os

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from pyweb_board.models import Board
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

    with open(path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet=stream')
        response['Content-Disposition'] = "attachment;filename*=UTF-8''{0}".format(filename)

    dto.down_up()
    dto.save()
    return response
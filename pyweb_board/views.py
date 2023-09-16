import math
import os
import urllib

from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from pyweb_board.models import Board, Comment
from django.http.response import HttpResponse

# Create your views here.
upload_dir = 'pyweb_board/static/upload/'

# 페이징 처리 추가 전
# def list(request):
#     boardCount = Board.objects.count()
#     boardList = Board.objects.all().order_by("-idx")
#     return render(request, "board/list.html",
#                   {"boardList": boardList, "boardCount": boardCount})

# 페이징 처리 추가
def list(request):
    # 검색 처리 - 검색 종료, 검색어 있을 때와 없을 때 처리
    try:
        search_option = request.POST['search_option']
    except:
        search_option = ''

    try:
        search = request.POST['search']
    except:
        search=''

    print(search)
    print(search_option)

    # 검색 결과에 따른 레코드 개수 계산
    # 필드명_contains = 값 : where 필드명 like '%값%'
    # count() : select count(*)
    if search_option == 'all':
        boardCount = Board.objects.filter(Q(writer__contains=search)
                                          | Q(title__contains=search)
                                          | Q(content__contains=search)).count()
    elif search_option == 'writer':
        boardCount = Board.objects.filter(Q(writer__contains=search)).count()
    elif search_option == 'title':
        boardCount = Board.objects.filter(Q(title__contains=search)).count()
    elif search_option == 'content':
        boardCount = Board.objects.filter(Q(content__contains=search)).count()
    else:
        boardCount = Board.objects.count()
    # 페이지 처리
    try:
        start = int(request.GET['start'])
    except:
        start = 0
    page_size = 5
    block_size = 5

    end = start + page_size

    total_page = math.ceil(boardCount / page_size)
    current_page = math.ceil((start + 1) / page_size)
    start_page = math.floor((current_page - 1) / block_size) * block_size + 1
    end_page = start_page + block_size - 1

    # 마지막 페이지가 토탈 페이지보다 클 경우 고려하여 보정
    if end_page > total_page:
        end_page = total_page

    print('total page: ', total_page)
    print('current page: ', current_page)
    print('start page: ', start_page)
    print('end page: ', end_page)

    # 프리뷰 리스트
    if start_page >= block_size:
        prev_list = (start_page - 2) * page_size
    else:
        prev_list = 0

    # 넥스트 리스트
    if end_page < total_page:
        nest_list = end_page * page_size
    else:
        next_list = 0

    if search_option == 'all':
        boardList = Board.objects.filter(Q(writer__contains=search)
                                         | Q(title__contains=search)
                                         | Q(content__contains=search)).order_by("-idx")[start:end]
    elif search_option == 'writer':
        boardList = Board.objects.filter(Q(writer__contains=search)).order_by("-idx")[start:end]
    elif search_option == 'title':
        boardList = Board.objects.filter(Q(title__contains=search)).order_by("-idx")[start:end]
    elif search_option == 'content':
        boardList = Board.objects.filter(Q(content__contains=search)).order_by("-idx")[start:end]
    else:
        boardList = Board.objects.all().order_by("-idx")[start:end]

    # link 태그를 미리 만들어
    links = []
    for i in range(start_page, end_page + 1):
        page_start = (i - 1) * page_size
        links.append("<a href='/list/?start=" + str(page_start) + "'>" + str(i) + "</a>")

    return render(request, 'board/list.html',
                 {"boardList": boardList,
                  "boardCount": boardCount,
                  "search_option": search_option,
                  "search": search,
                  "range": range(start_page - 1, end_page),
                  "start_page": start_page,
                  "end_page": end_page,
                  "total_page": total_page,
                  "prev_list": prev_list,
                  "next_list": next_list,
                  "links": links})


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

from flask import Blueprint, redirect, render_template, request, url_for
from playlists.model.playlist_edit_model import PlaylistEditModel
from playlists.model.playlist_detail_model import PlaylistDetailModel
from services.content_service import ContentService

playlists_bp = Blueprint(
    "playlists", __name__, 
    template_folder="templates", 
    static_folder="static"
)

content_service = ContentService()

@playlists_bp.route("/")
def playlists_index():
    playlists = content_service.get_playlists()
    return render_template("playlists_index.html", model=playlists)

@playlists_bp.route("/add", methods=["GET", "POST"])
def playlist_add():
    if request.method == "POST":
        content_service.create_playlist(
            name=request.form["name"],
            short_name=request.form["short_name"],
            description=request.form["description"]
        )
        return redirect(url_for('playlists.playlists_index'))
    
    elif request.method == "GET":
        return render_template("playlists_add.html")

@playlists_bp.route("/<playlist_id>")
def playlist_detail(playlist_id):
    playlist = content_service.get_playlist_with_contents(id=playlist_id)
    return render_template("playlists_detail.html", model=playlist)

@playlists_bp.route("edit/<playlist_id>", methods=["GET", "POST"])
def playlist_edit(playlist_id):
    if request.method == "POST":
        
        content_service.update_playlist(
            id=playlist_id,
            name=request.form["name"],
            short_name=request.form["short_name"],
            description=request.form["description"]
        )
        
        return redirect(url_for('playlists.playlist_detail', playlist_id=playlist_id))
    
    elif request.method == "GET":
        playlist = content_service.get_playlist(id=playlist_id)
        content_info_list = []
        for content_info in playlist["content"]:
            content = content_service.get_content(content_id=content_info["id"])
            content_info_list.append(
                { 
                 "id": content["id"], 
                 "title": content["title"],
                "display_order": content_info["display_order"]
                }
            )
    
    model=PlaylistEditModel(content_info_items=content_info_list, playlist=playlist)

    return render_template("playlists_edit.html", model=model)

@playlists_bp.route("playlist_order/<playlist_id>", methods=["POST"])
def playlist_order_update(playlist_id):
    sorted_content_items = request.json
    
    try:
        content_service.update_playlist_content_display_order(
            playlist_id=playlist_id,
            content_items=sorted_content_items
        )
        return "", 200
    except Exception as e:
        print(e)
        return "", 500
        


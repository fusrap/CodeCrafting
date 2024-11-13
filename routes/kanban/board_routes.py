from flask import Blueprint, jsonify, request
from routes.base_route import BaseRoute
from models import KanbanBoards

kanban_bp = Blueprint("kanban", __name__)

class BoardRoutes(BaseRoute):
    model = KanbanBoards

    def to_dict(self, instance):
        """Convert instance data to a dictionary format for JSON responses."""
        return {
            "board_id": instance.board_id,
            "title": instance.title,
            "description": instance.description
        }


    @kanban_bp.route("/boards", methods=["POST"])
    def create_board():
        data = request.get_json()
        if "title" not in data:
            return jsonify({"error": "Title is required"}), 400  

        board_routes = BoardRoutes()
        new_board = board_routes.create(data) 

        if isinstance(new_board, dict) and "error" in new_board:
            return jsonify(new_board), 500

        return jsonify({
            "message": "Board created successfully",
            "board_id": new_board.board_id,
            "title": new_board.title,
            "description": new_board.description
        }), 201

    @kanban_bp.route("/boards", methods=["GET"])
    def get_all_boards():
        board_routes = BoardRoutes()
        print("Calling get_all() method")  # Debug statement
        boards, status_code = board_routes.get_all()
        print("Received data from get_all()", boards)  # Debug statement

        boards_dict = [board_routes.to_dict(board) for board in boards]
        return jsonify(boards_dict), status_code

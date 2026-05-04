import sys
import math
import json # Sửa lỗi "json is not defined"
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from graph_engine import GraphEngine

class GraphApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ĐỒ ÁN ĐỒ THỊ FINAL - NGUYỄN THIÊN PHÚ - UTH")
        self.setGeometry(30, 30, 1280, 850)
        
        # Khởi tạo Engine
        self.engine = GraphEngine(is_directed=True)
        self.nodes_pos = {}
        self.selected_node = None
        self.mode = "NODE"
        self.highlighted_edges = []
        self.timer = QTimer()
        
        self.initUI()

    def initUI(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QHBoxLayout(widget)

        # Thanh Menu chứa tất cả yêu cầu từ image_c2fcfe.png
        panel = QVBoxLayout()
        self.lbl_info = QLabel("CHẾ ĐỘ: THÊM ĐỈNH")
        self.lbl_info.setStyleSheet("font-weight: bold; color: #e67e22; font-size: 14px;")
        panel.addWidget(self.lbl_info)

        options = [
            ("❶ Thêm Đỉnh (Mục 1)", lambda: self.set_mode("NODE")),
            ("❷ Nối Cạnh (Có hướng)", lambda: self.set_mode("EDGE")),
            ("❸ Duyệt BFS (Mục 4)", lambda: self.run_sim("bfs")),
            ("❹ Duyệt DFS (Mục 4)", lambda: self.run_sim("dfs")),
            ("❺ Kiểm tra 2 phía (Mục 5)", self.check_bi),
            ("❻ Biểu diễn đồ thị (Mục 6)", self.show_conv),
            ("❼ Thuật toán Prim (7.1)", lambda: self.run_sim("prim")),
            ("❽ Thuật toán Kruskal (7.2)", lambda: self.run_sim("kruskal")),
            ("❾ Ford-Fulkerson (7.3)", self.run_ff),
            ("❿ Thuật toán Fleury (7.4)", lambda: self.run_sim("euler")),
            ("⓫ Hierholzer (7.5)", lambda: self.run_sim("euler")),
            ("⓬ Lưu đồ thị (Mục 2)", self.save_data)
        ]

        for text, func in options:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.clicked.connect(func)
            panel.addWidget(btn)
        
        panel.addStretch()

        # Canvas vẽ đồ thị
        self.canvas = QLabel()
        self.canvas.setStyleSheet("background: white; border: 3px solid #2c3e50; border-radius: 10px;")
        self.canvas.setMinimumWidth(900)
        
        layout.addLayout(panel, 1)
        layout.addWidget(self.canvas, 4)

    def set_mode(self, m):
        self.mode = m
        self.selected_node = None
        self.lbl_info.setText(f"CHẾ ĐỘ: {m}")

    def mousePressEvent(self, event):
        p = self.canvas.mapFromParent(event.pos())
        x, y = p.x(), p.y()
        if not (0 <= x <= self.canvas.width() and 0 <= y <= self.canvas.height()): return
        
        target = self.get_node_at(x, y)
        if self.mode == "NODE" and target is None:
            nid = len(self.nodes_pos)
            self.nodes_pos[nid] = (x, y)
            self.engine.graph.add_node(nid)
        elif self.mode == "EDGE" and target is not None:
            if self.selected_node is None: self.selected_node = target
            else:
                self.engine.add_edge(self.selected_node, target)
                self.selected_node = None
        self.update_drawing()

    def get_node_at(self, x, y):
        for nid, (nx, ny) in self.nodes_pos.items():
            if math.sqrt((x-nx)**2 + (y-ny)**2) < 20: return nid
        return None

    def update_drawing(self, high=False):
        pix = QPixmap(self.canvas.size())
        pix.fill(Qt.white)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Vẽ cạnh kèm mũi tên
        for u, v in self.engine.graph.edges():
            p1, p2 = self.nodes_pos[u], self.nodes_pos[v]
            if high and ((u, v) in self.highlighted_edges or (v, u) in self.highlighted_edges):
                painter.setPen(QPen(Qt.red, 4))
            else:
                painter.setPen(QPen(Qt.black, 2))
            painter.drawLine(p1[0], p1[1], p2[0], p2[1])

        # Vẽ đỉnh
        for nid, (nx, ny) in self.nodes_pos.items():
            color = Qt.green if nid == self.selected_node else QColor("#3498db")
            painter.setBrush(QBrush(color))
            painter.drawEllipse(nx-18, ny-18, 36, 36)
            painter.setPen(Qt.white)
            painter.drawText(nx-6, ny+5, str(nid))
        painter.end()
        self.canvas.setPixmap(pix)

    def run_sim(self, algo):
        self.highlighted_edges = []
        if len(self.nodes_pos) == 0: return
        
        if algo == "bfs": edges = self.engine.get_bfs_edges(0)
        elif algo == "dfs": edges = self.engine.get_dfs_edges(0)
        elif algo == "prim": edges = self.engine.get_prim_edges()
        elif algo == "kruskal": edges = self.engine.get_kruskal_edges()
        elif algo == "euler": edges = self.engine.get_euler_circuit()
        else: return

        self.step = 0
        try: self.timer.timeout.disconnect()
        except: pass
        self.timer.timeout.connect(lambda: self.next_sim_step(edges))
        self.timer.start(700)

    def next_sim_step(self, edges):
        if self.step < len(edges):
            u, v = edges[self.step][0], edges[self.step][1]
            self.highlighted_edges.append((u, v))
            self.update_drawing(True)
            self.step += 1
        else: self.timer.stop()

    def run_ff(self):
        if len(self.nodes_pos) < 2: return
        val = self.engine.get_max_flow_ff(0, len(self.nodes_pos)-1)
        QMessageBox.information(self, "7.3 Ford-Fulkerson", f"Luồng cực đại từ 0 đến {len(self.nodes_pos)-1}: {val}")

    def show_conv(self):
        m, _, _ = self.engine.get_conversions()
        QMessageBox.information(self, "Mục 6", f"Ma trận kề:\n{m}")

    def check_bi(self):
        res = self.engine.is_bipartite()
        QMessageBox.information(self, "Mục 5", f"Đồ thị 2 phía: {'ĐÚNG' if res else 'SAI'}")

    def save_data(self):
        with open("dothi_phu_final.json", "w") as f:
            json.dump({"nodes": self.nodes_pos, "edges": list(self.engine.graph.edges())}, f)
        QMessageBox.information(self, "Mục 2", "Đã lưu đồ thị thành công!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphApp()
    window.show()
    sys.exit(app.exec_())
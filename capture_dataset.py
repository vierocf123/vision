import cv2
import os
import time
from datetime import datetime

class DatasetCollector:
    def __init__(self, base_path, class_name, camera_index):
        # Configuração de caminhos no Drive E:
        self.class_name = class_name
        self.save_path = os.path.join(base_path, 'data', 'raw', class_name)
        os.makedirs(self.save_path, exist_ok=True)
        
        self.win_live = "1. AO VIVO (MIRA)"
        self.win_last = "2. ULTIMA FOTO (Z = ZOOM)"
        self.w, self.h = 480, 270 
        
        # Estado do Zoom
        self.zoom_ativo = False
        
        # Inicialização da Câmera
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        self.count = 0
        self.last_saved_frame = None

    def desenhar_mira(self, img):
        """Mantém o enquadramento e a mira sempre visíveis."""
        h, w = img.shape[:2]
        cx, cy = w // 2, h // 2
        # Mira verde central
        cv2.line(img, (cx - 15, cy), (cx + 15, cy), (0, 255, 0), 1)
        cv2.line(img, (cx, cy - 15), (cx, cy + 15), (0, 255, 0), 1)
        # Retângulo de enquadramento (Safe Zone)
        cv2.rectangle(img, (cx - 120, cy - 120), (cx + 120, cy + 120), (200, 200, 200), 1)
        return img

    def run(self):
        if not self.cap.isOpened():
            print("[ERRO] Verifique a conexão da câmera.")
            return

        # Setup de Janelas
        cv2.namedWindow(self.win_live, cv2.WINDOW_NORMAL)
        cv2.namedWindow(self.win_last, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.win_live, self.w, self.h)
        cv2.resizeWindow(self.win_last, self.w, self.h)
        cv2.moveWindow(self.win_live, 50, 50)
        cv2.moveWindow(self.win_last, 540, 50)

        print(f"\n[INFO] Direitório: {self.save_path}")
        print("ATALHOS: [S] Salvar | [Z] Alternar Zoom | [Q] Sair")

        while True:
            ret, frame = self.cap.read()
            if not ret: break

            # Janela 1: Sempre com Mira e Enquadramento
            live_view = cv2.resize(frame, (self.w, self.h))
            live_view = self.desenhar_mira(live_view)
            cv2.putText(live_view, f"FOTOS: {self.count}", (10, 25), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            cv2.imshow(self.win_live, live_view)
            cv2.setWindowProperty(self.win_live, cv2.WND_PROP_TOPMOST, 1)

            # Janela 2: Lógica de Zoom Manual
            if self.last_saved_frame is not None:
                if self.zoom_ativo:
                    # Aplica o Zoom (300x300 no centro)
                    h_orig, w_orig = self.last_saved_frame.shape[:2]
                    cx, cy = w_orig // 2, h_orig // 2
                    crop = self.last_saved_frame[cy-150:cy+150, cx-150:cx+150]
                    display_frame = cv2.resize(crop, (self.w, self.h))
                    status_txt = "MODO: ZOOM"
                else:
                    # Mostra a foto inteira normalmente
                    display_frame = cv2.resize(self.last_saved_frame, (self.w, self.h))
                    status_txt = "MODO: INTEIRA"

                cv2.putText(display_frame, status_txt, (10, 25), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.imshow(self.win_last, display_frame)
                cv2.setWindowProperty(self.win_last, cv2.WND_PROP_TOPMOST, 1)
            
            # Processamento de Teclas
            key = cv2.waitKey(1) & 0xFF
            
            # Tecla Z: Inverte o estado do zoom
            if key == ord('z') or key == ord('Z'):
                self.zoom_ativo = not self.zoom_ativo
                estado = "ATIVADO" if self.zoom_ativo else "DESATIVADO"
                print(f"[*] Zoom {estado}")

            elif key == ord('s') or key == ord('S'):
                ts = datetime.now().strftime("%H%M%S_%f")
                fname = f"{self.class_name}_{ts}.jpg"
                if cv2.imwrite(os.path.join(self.save_path, fname), frame):
                    self.count += 1
                    self.last_saved_frame = frame.copy()
                    print(f">>> Foto {self.count} salva no Drive E:")

            elif key == ord('q') or key == ord('Q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    BASE = r"E:\eFact\Fotos_Data_Set"
    CLASSE = "produto_v01"
    app = DatasetCollector(BASE, CLASSE, 0)
    app.run()
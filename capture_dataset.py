import cv2
import os
import time
from datetime import datetime

def detectar_cameras():
    print("\n" + "="*50)
    print("      SCANNER DE HARDWARE (CAMERA)      ")
    print("="*50)
    indices = []
    for i in range(5):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                print(f"[ DISPONÍVEL ] -> Índice {i}")
                indices.append(i)
            cap.release()
    return indices

class DatasetCollector:
    def __init__(self, base_path, class_name, camera_index):
        self.class_name = class_name
        self.save_path = os.path.join(base_path, 'data', 'raw', class_name)
        os.makedirs(self.save_path, exist_ok=True)
        
        self.win_live = "1. AO VIVO (FOCO AQUI)"
        self.win_last = "2. ULTIMA FOTO SALVA"
        self.w, self.h = 480, 270 
        
        # Inicializa a câmera
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) 
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        self.count = 0
        self.last_saved_frame = None

    def run(self):
        if not self.cap.isOpened():
            print("\n[ERRO] Câmera inacessível.")
            return

        # --- SEQUÊNCIA DE BOOT DE JANELAS (LADO A LADO) ---
        # 1. Cria e redimensiona
        cv2.namedWindow(self.win_live, cv2.WINDOW_NORMAL)
        cv2.namedWindow(self.win_last, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.win_live, self.w, self.h)
        cv2.resizeWindow(self.win_last, self.w, self.h)

        # 2. Posiciona no topo da tela
        cv2.moveWindow(self.win_live, 50, 50)
        cv2.moveWindow(self.win_last, 550, 50) 

        # 3. Força a exibição imediata para o Windows não as esconder
        ret, first_frame = self.cap.read()
        if ret:
            blank = cv2.resize(first_frame, (self.w, self.h)) * 0
            cv2.imshow(self.win_live, blank)
            cv2.imshow(self.win_last, blank)
            # Traz ambas para frente de tudo
            cv2.setWindowProperty(self.win_live, cv2.WND_PROP_TOPMOST, 1)
            cv2.setWindowProperty(self.win_last, cv2.WND_PROP_TOPMOST, 1)
            cv2.waitKey(500) # Pequena pausa para o Windows processar o layout

        print(f"\n[SUCESSO] Janelas iniciadas lado a lado.")

        while True:
            ret, frame = self.cap.read()
            if not ret: break

            # Janela 1: Ao Vivo
            live_view = cv2.resize(frame, (self.w, self.h))
            cv2.putText(live_view, f"Fotos: {self.count}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.imshow(self.win_live, live_view)

            # Janela 2: Última Salva
            if self.last_saved_frame is not None:
                last_view = cv2.resize(self.last_saved_frame, (self.w, self.h))
                cv2.imshow(self.win_last, last_view)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s') or key == ord('S'):
                ts = datetime.now().strftime("%H%M%S_%f")
                fname = f"{self.class_name}_{ts}.jpg"
                if cv2.imwrite(os.path.join(self.save_path, fname), frame):
                    self.count += 1
                    feedback = frame.copy()
                    cv2.putText(feedback, "SALVO!", (50, 200), 
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
                    self.last_saved_frame = feedback
                    print(f">>> [{self.count}] Salva com sucesso!", flush=True)

            elif key == ord('q') or key == ord('Q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Garanta que o terminal está com o (.venv) ativo
    indices = detectar_cameras()
    if indices:
        try:
            val = input("\nDIGITE O INDICE DA CAMERA E ENTER: ")
            escolha = int(val)
            # Caminho absoluto para o drive E:
            app = DatasetCollector(r"E:\eFact\Fotos_Data_Set", "produto_v01", escolha)
            app.run()
        except Exception as e:
            print(f"Erro: {e}")
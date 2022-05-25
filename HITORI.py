import g2d
from time import time
import datetime
from random import randrange, randint

W, H = 40, 40
LONG_PRESS = 0.5
NERO = "BLACK"
BIANCO = "CLEAR"
CERCHIO = "CIRCLE"


# gui
class BoardGameGui:
    def __init__(self, g):
        self._game = g
        self._downtime = 0
        self._wrong = False
        self._inpartita = False
        self.update_buttons()
        self._mosse = 0  # variabile incrementata ad ogni mossa del giocatore

    def tick(self):
        if self._inpartita:
            if g2d.key_pressed("LeftButton"):
                self._downtime = time()
            elif g2d.key_released("LeftButton"):
                mouse = g2d.mouse_position()
                self._mosse += 1
                x, y = mouse[0] // W, mouse[1] // H
                if time() - self._downtime > LONG_PRESS:
                    self._game.flag_at(x, y)
                    self.update_buttons()
                else:
                    self._game.play_at(x, y)
                    self.update_buttons()
            if g2d.key_pressed(
                    "Spacebar"):  # premendo Spacebar vengono cerchiate automaticamente le celle adiacenti a celle nere gia marcate
                self._mosse += 1
                self._game.cerc_auto()
                self.update_buttons()
            if g2d.key_pressed(
                    "ArrowUp"):  # premendo ArrowUp vengono marcate automaticamente le celle che si trovano nella stessa riga o colonna di una cella cerchiata
                self._mosse += 1
                self._game.mark_auto()
                self.update_buttons()
        elif g2d.key_pressed("Enter"):
            if self._inpartita:
                self._mosse += 1
            self._inpartita = True
            self.update_buttons()

    def update_buttons(self):
        g2d.clear_canvas()
        g2d.set_color((5, 255, 55))
        cols, rows = self._game.cols(), self._game.rows()
        if self._inpartita:
            for y in range(1, rows):
                g2d.draw_line((0, y * H), (cols * W, y * H))
            for x in range(1, cols):
                g2d.draw_line((x * W, 0), (x * W, rows * H))
            for y in range(rows):
                for x in range(cols):
                    value = self._game.value_at(x, y)
                    center = x * W + W // 2, y * H + H // 2
                    x1, y1 = center
                    if value[-1] == "#":
                        g2d.set_color((0, 0, 0))
                        g2d.fill_rect((x1 - 20, y1 - 20, W, H))
                    elif value[-1] == "!":
                        g2d.fill_circle(center, H // 2)
                        g2d.set_color((255, 255, 255))
                        g2d.fill_circle(center, H // 2 - 1)
                    g2d.set_color((0, 0, 0))
                    g2d.draw_text_centered(value[:-1], center, H // 2)
        else:
            g2d.draw_text('Hitori', (110, 20), 40)
            g2d.draw_text('Premi INVIO per iniziare', (20, 100), 25)
        g2d.update_canvas()
        if self._game.finished():
            g2d.alert(self._game.message() + " con " + str(self._mosse) + " mosse")
            g2d.close_canvas()
        if self._game.wrong() and self._inpartita:
            g2d.alert("Errato!")


def gui_play(game):
    g2d.init_canvas((game.cols() * W, game.rows() * H))
    ui = BoardGameGui(game)
    g2d.main_loop(ui.tick)


# game
class HitoriGame:
    def __init__(self, lato=8):
        self._board = []
        with open("matrix.txt") as file1:
            for riga in file1:
                riga = riga.strip()
                self._board.append(riga.split(","))
        self._etichetta = [[BIANCO for y in range(lato)] for x in range(lato)]
        self.colonne, self.righe = lato, lato
        self._starttime = datetime.datetime.now()

    def cols(self) -> int:
        return self.colonne

    def rows(self) -> int:
        return self.righe

    def continuity(self, i, x,
                   matrix) -> int:  # verifica che tutte le caselle bianche siano continue cioe che non ci siano zone isolate
        totale = 1
        x = x
        y = i
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            x1, y1 = x + dx, y + dy
            if 0 <= x1 < self.colonne and 0 <= y1 < self.righe:
                if self._etichetta[y1][x1] != NERO and not matrix[y1][x1]:
                    matrix[y1][x1] = True
                    totale += self.continuity(y1, x1, matrix)
        return totale

    def finished(self) -> bool:  # controlla che tutte le condizioni di vittoria siano soddisfatte
        contatore = 0
        for y in range(self.righe):
            for x in range(self.colonne):
                val = self._board[y][x]
                if self._etichetta[y][x] != NERO:
                    contatore += 1

                    for i in range(self.righe):
                        if self._etichetta[i][x] != NERO:
                            if val == self._board[i][x] and i != y:
                                return False

                    for i in range(self.colonne):
                        if self._etichetta[y][i] != NERO:
                            if val == self._board[y][i] and i != x:
                                return False

                elif self._etichetta[y][x] == NERO:
                    for dx, dy in ((0, -1), (0, 1), (1, 0), (-1, 0)):
                        x1, y1 = x + dx, y + dy
                        if 0 <= x1 < self.righe and 0 <= y1 < self.colonne:
                            if self._etichetta[y1][x1] == NERO:
                                return False

        matrix = [[False for x in range(self.righe)] for y in range(self.colonne)]
        tmp = 0
        trovato = False
        while trovato is False:
            if self._etichetta[tmp][0] == BIANCO:
                matrix[tmp][0] = True
                trovato = True
                continuity = self.continuity(tmp, 0, matrix)
                print(continuity, contatore)  # stampo caselle continue e caselle bianche
                if continuity != contatore:
                    return False
            tmp += 1
        return True

    def play_at(self, x: int, y: int):
        if 0 <= x < self.colonne and 0 <= y < self.righe:
            if self._etichetta[y][x] != NERO:
                self._etichetta[y][x] = NERO
            elif self._etichetta[y][x] == NERO:
                self._etichetta[y][x] = BIANCO

    def cerc_auto(self):
        for y in range(self.righe):
            for x in range(self.colonne):
                if self._etichetta[y][x] == NERO:
                    for dx, dy in ((0, -1), (0, 1), (1, 0), (-1, 0)):
                        x1, y1 = x + dx, y + dy
                        if 0 <= x1 < self.righe and 0 <= y1 < self.colonne:
                            self._etichetta[y1][x1] = CERCHIO

    def wrong(self) -> bool:  # metodo che segnala la presenza di un errore in fase di risoluzione del gioco
        contatore = 0
        for y in range(self.righe):
            for x in range(self.colonne):
                val = self._board[y][x]
                if self._etichetta[y][x] == NERO:
                    for dx, dy in ((0, -1), (0, 1), (1, 0), (-1, 0)):
                        x1, y1 = x + dx, y + dy
                        if 0 <= x1 < self.righe and 0 <= y1 < self.colonne:
                            if self._etichetta[y1][x1] == NERO:
                                return True
                elif self._etichetta[y][x] == CERCHIO:
                    contatore += 1
                    for i in range(self.righe):
                        if self._etichetta[i][x] == CERCHIO:
                            if val == self._board[i][x] and i != y:
                                return True

                    for i in range(self.colonne):
                        if self._etichetta[y][i] == CERCHIO:
                            if val == self._board[y][i] and i != x:
                                return True
                elif self._etichetta[y][x] == BIANCO:
                    contatore += 1
        matrix = [[False for x in range(self.righe)] for y in range(self.colonne)]
        i = 0
        stopwhile = False
        while not stopwhile:
            if self._etichetta[i][0] != NERO:
                stopwhile = True
                matrix[i][0] = True
                continuity = self.continuity(i, 0, matrix)
                if continuity != contatore:
                    return True
            i += 1
        return False

    def mark_auto(self):
        for y in range(self.righe):
            for x in range(self.colonne):
                if self._etichetta[y][x] == CERCHIO:
                    pos = self._board[y][x]

                    for i in range(self.righe):
                        if pos == self._board[i][x] and i != y:
                            self._etichetta[i][x] = NERO

                    for k in range(self.colonne):
                        if pos == self._board[y][k] and k != x:
                            self._etichetta[y][k] = NERO

    def flag_at(self, x: int, y: int):
        if self._etichetta[y][x] != CERCHIO:
            self._etichetta[y][x] = CERCHIO
        elif self._etichetta[y][x] == CERCHIO:
            self._etichetta[y][x] = BIANCO

    def value_at(self, x: int, y: int):
        if 0 <= x < self.colonne and 0 <= y < self.righe:
            if self._etichetta[y][x] == NERO:
                return str(self._board[y][x]) + "#"
            elif self._etichetta[y][x] == CERCHIO:
                return str(self._board[y][x]) + "!"
            return str(self._board[y][x]) + "$"

    def message(self) -> str:
        self._time = str((datetime.datetime.now() - self._starttime))[2:-7]
        finalstr = "Gioco Completato in " + self._time
        return finalstr


def main():
    game = HitoriGame()
    gui_play(game)


main()

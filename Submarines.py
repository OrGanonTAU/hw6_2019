import numpy as np
import random

class Game():
    """
    you just lost the game.
    
    """
    def __init__(
        self, x_len=8, y_len=8, z_len=3, sub_num=1, des_num=1, jet_num=1
    ): 
        """
        Makes 2 boards
        """
        self.board1 = Board(x_len, y_len, z_len, sub_num, des_num, jet_num)
        self.board2 = Board(x_len, y_len, z_len, sub_num, des_num, jet_num)
        print ("Boards are set")


    def start(self): 
        current_player = 'player 1'
        current_board = self.board1
        other_player = 'player 2'
        other_board = self.board2
        while True:
            self.print_status(current_board, other_board)
            coord = self.get_coord(current_player,current_board)
            if coord == "quit":
                print("Bye !")
                break

            result = other_board.hit_coord(coord)
            print(result)

            # end loop if win
            if self.ended(other_board):
                print(f"{current_player} Won!")
                break

            # switch players
            current_player, other_player = other_player, current_player
            current_board, other_board = other_board, current_board


    def ended(self, other_board):
        if other_board.general_dead():
            return True
        if other_board.all_units_dead():
            return True
        return False


    def print_status(self, current_board, other_board):
        print("my board")
        current_board.show()
        print("battlefield")
        other_board.show(hidden=True)

    def get_coord(self, current_player, current_board):
        #ask and check input. 
        while True: 
            try:
                command = input(
                    f"{current_player}, what coordinates do you target? (x,y,z) "
                )
                if command.lower() == "quit":
                    return command.lower()
                elif command.lower() == "show":
                    print("my board")
                    current_board.show()

                    continue
                current_player_fire = command.replace("[","").replace("]","").replace("(","").replace(")","").split(",",3)
                new_coor=tuple([int(num) for num in current_player_fire])
                assert(0<=new_coor[0]<current_board.x_len and 0<=new_coor[1]<current_board.y_len and 0<=new_coor[2]<current_board.z_len)
                return new_coor
            except (AssertionError,ValueError):
                print ("not a valid coordinate")
                continue

        


# #making the board:
class Board:
    """
    Crearts a board according to specific size and amount of tools.
    The order is as folowing: x axis length , y axis length, z axis length (should be 3),
    amount of submarines, amount of destroyers and the amount of jets.
    """
    def __init__(self, x_len=8, y_len=8, z_len=3, sub_num=3, des_num=1, jet_num=1):
        self.x_len = x_len
        self.y_len = y_len
        self.z_len = z_len

        self.touched_coords=[] #keeps all trails 
       
        # here all coordnates will be added:
        vessel_list = []

        def is_collision(coordinates, vessel_list):
            for vessel in vessel_list:
                for coord in coordinates:
                    if vessel.is_inside(coord):
                        return True
            return False

        vessels_to_add = [
            (Submarine, sub_num), 
            (Destroyer, des_num), 
            (Jet, jet_num), 
            (General, 1),
        ]

        for vessel_type, vessel_num in vessels_to_add:
            for s in range(vessel_num):
                sub = vessel_type(x_len, y_len, z_len)
                tries = 0 
                while is_collision(sub.coordinates, vessel_list):
                    sub = vessel_type(x_len, y_len, z_len)
                    tries += 1
                    if tries > 30:
                        raise RuntimeError("can't create board")
                vessel_list.append(sub)

        self.vessel_list = vessel_list


    def to_mat(self):
        """
        represent the board
        """
        board_mat = np.zeros((self.x_len, self.y_len, self.z_len), int)
        for ves in self.vessel_list:
            for coor in ves.coordinates:
                board_mat[coor] = -1 if ves.coords_is_hit[coor] else 1
        return board_mat


    def show(self, hidden=False):
        """
        shows the boards
        """
        mat = self.to_mat()

        x_len, y_len, z_len = mat.shape
        for y in range(y_len):
            print(y, end = '  ')
            for z in range(z_len):
                for x in range(x_len):
                    if hidden and (x, y, z) not in self.touched_coords:
                        print("?", end='')
                    elif mat[x, y, z] == 1:
                        print('*', end='')
                    elif mat[x, y, z] == -1:
                        print('x', end='')
                    elif mat[x, y, z] == 0:
                        print('.', end='')
                    print(' ', end='')
                print ('\t', end='')
            print()
        print()


    
    def hit_coord(self, coord):
        self.touched_coords.append(coord)
        for vess in self.vessel_list:
            if vess.is_inside(coord):
                result = vess.hit(coord)
                if result == "KILL!":
                    self.touched_coords += vess.coordinates
                return result
        return "MISS!"
        

    def general_dead(self):
        """
        checks for dead generals
        """
        for vess in self.vessel_list:
            if isinstance(vess,General):
                if not vess.is_alive():
                    return True
        return False


    def all_units_dead(self):
        """
        checks if all the non-general vessel are dead
        """
        for vess in self.vessel_list:
            if not isinstance(vess,General):
                if vess.is_alive():
                    return False
        return True



######################

# making the vessels:

class Vessel:
    # one hit = will the vessel die after 1 hit?

    def __init__(self, coordinates, one_hit=True):
        self.one_hit = one_hit
        self.coordinates = coordinates
        self.coords_is_hit = {c: False for c in coordinates}

    def is_inside(self, coord):
        return coord in self.coordinates

    def hit(self, coord):
        if not self.is_alive():
            return "ALREADY DEAD!"
        if self.coords_is_hit[coord]:
            return "ALREADY DAMAGED HERE!"
        self.coords_is_hit[coord] = True
        if self.one_hit:
            self.coords_is_hit = {c: True for c in self.coords_is_hit}
            return "KILL!"
        else:
            if self.is_alive():
                return "HIT!"
            else:
                return "KILL!"

    def is_alive(self):
        return (not all(self.coords_is_hit.values()))
        



    # def got_hit (self,  )
    #     if one_hit:

    #     else:

    # def new_vessel_type(self, name, one_hit=1, size):

    # def hit (): #here or in the game?
    #     if attempt== coordinates:

class Submarine(Vessel):
    # size =3 (1,1,1), one hit kill
    def __init__(self, x_len, y_len, z_len):
        # find coordinates, for now it's just random
        what_dir = random.randint(0, 3)
        if what_dir == 0:
            head = (random.randint(0, x_len-1), random.randint(0, (y_len - 2)-1), 0)
            mid = (head[0], head[1] + 1, 0)
            tail = (head[0], head[1] + 2, 0)
        elif what_dir == 1:
            head = (random.randint(0, x_len-1), random.randint(2, y_len-1), 0)
            mid = (head[0], head[1] - 1, 0)
            tail = (head[0], head[1] - 2, 0)
        elif what_dir == 2:
            head = (random.randint(0, (x_len - 2)-1), random.randint(0, y_len-1), 0)
            mid = (head[0] + 1, head[1], 0) 
            tail = (head[0] + 2, head[1], 0)
        else:
            head = (random.randint(2, x_len-1), random.randint(0, y_len-1), 0)
            mid = (head[0] - 1, head[1], 0)
            tail = (head[0] - 2, head[1], 0)

        super().__init__(coordinates=[head, mid, tail], one_hit=True)

class Destroyer (Vessel):
    # size =4 (1,1,1,1),sevral hits kill
    def __init__(self, x_len, y_len, z_len):
        # find coordinates, for now it's just random
        what_dir = random.randint(0, 3)
        if what_dir == 0:
            head = (random.randint(0, x_len-1), random.randint(0, (y_len - 3)-1), 1)
            mid = (head[0], head[1] + 1, 1)
            mid2 = (head[0], head[1] + 2, 1)
            tail = (head[0], head[1] + 3, 1)
        elif what_dir == 1:
            head = (random.randint(0, x_len-1), random.randint(3, y_len-1), 1)
            mid = (head[0], head[1] - 1, 1)
            mid2 = (head[0], head[1] - 2, 1)
            tail = (head[0], head[1] - 3, 1)
        elif what_dir == 2:
            head = (random.randint(0, (x_len - 3)-1), random.randint(0, y_len-1), 1)
            mid = (head[0] + 1, head[1], 1)
            mid2 = (head[0] + 2, head[1], 1)
            tail = (head[0] + 3, head[1], 1)
        else:
            head = (random.randint(3, x_len-1), random.randint(0, y_len-1), 1)
            mid = (head[0] - 1, head[1], 1)
            mid2 = (head[0] - 2, head[1], 1)
            tail = (head[0] - 3, head[1], 1)

        super().__init__(coordinates=[head, mid, mid2, tail], one_hit=False)

class Jet (Vessel):
 #          0,1,0,0
 # size =4 (1,1,1,1),sevral hits kill
 #          0,1,0,0
    def __init__(self, x_len, y_len, z_len):
        # find coordinates, for now it's just random
        what_dir = random.randint(0, 3)
        if what_dir == 0:
            head = (random.randint(1, (x_len-1)-1), random.randint(0, (y_len - 3)-1), 2)
            mid = (head[0], head[1] + 1, 2)
            mid_right = (head[0]+1, head[1] + 1, 2)
            mid_left = (head[0]-1, head[1] + 1, 2)
            mid2 = (head[0], head[1] + 2, 2)
            tail = (head[0], head[1] + 3, 2)
        elif what_dir == 1:
            head = (random.randint(1, (x_len-1)-1), random.randint(3, y_len-1), 2)
            mid = (head[0], head[1] - 1, 2)
            mid_right = (head[0]+1, head[1] - 1, 2)
            mid_left = (head[0]-1, head[1] - 1, 2)
            mid2 = (head[0], head[1] - 2, 2)
            tail = (head[0], head[1] - 3, 2)
        elif what_dir == 2:
            head = (random.randint(0, (x_len - 3)-1), random.randint(1, (y_len-1)-1), 2)
            mid = (head[0] + 1, head[1], 2)
            mid_right = (head[0] + 1, head[1]+1, 2)
            mid_left = (head[0] + 1, head[1]-1, 2)
            mid2 = (head[0] + 2, head[1], 2)
            tail = (head[0] + 3, head[1], 2)
        else:
            head = (random.randint(3, x_len-1), random.randint(1, y_len-1), 2)
            mid = (head[0] - 1, head[1], 2)
            mid_right = (head[0] - 1, head[1]+1, 2)
            mid_left = (head[0] - 1, head[1]-1, 2)
            mid2 = (head[0] - 2, head[1], 2)
            tail = (head[0] - 3, head[1], 2)

        super().__init__(coordinates=[head, mid, mid_right, mid_left, mid2, tail], one_hit=True)

class General(Vessel):
    # size =1 (1), one hit ends the game,  can be in any plain.
     def __init__(self, x_len, y_len, z_len):
        # find coordinates, for now it's just random
        head = (random.randint(0, x_len-1), random.randint(0, y_len -1), random.randint(0, z_len -1))

        super().__init__(coordinates=[head], one_hit=True)


###########
if __name__ == "__main__":
    # board = Board(8, 8, 3, 4, 2, 2)
    # board.show()
    # print(board.vessel_list[8].coordinates)

    g=Game(x_len=6, y_len=6, z_len=3, sub_num=4, des_num=3, jet_num=2)
    g.start()
import pickle
import room1, room2, room3, room4

num = room4.num
obj = room4.obj

with open(f"rooms/room{num}.bin", "wb") as pickle_in:
    pickle.dump(obj, pickle_in, pickle.HIGHEST_PROTOCOL)
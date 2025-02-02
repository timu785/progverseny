import random
import math
import os

cheats:bool = False
fuel:int = 2
max_fuel:int = 2
credits:float = random.randrange(30, 81)
goods:int = 0
max_goods:int = 5
equipment:str = []
# hol vagyunk a térképen, vagyis a térkép lista indexe
location:int = 0
# térkép, vagyis bolygók listája, az űrt 3*_-al jelöljük
map:str = ["Thorodin", "Ydalir", "Vidar", "___", "Folkvang"]
# az adott indexű bolygó technikaifejlettsége, min 1 és max 15, az űrt 0-val jelöljük
tech_map:int = [2, 4, 10, 0, 6]
# az adott indexű bolygónak van-e teleszkópja, az űr egyértelműen mindig False
telescope_map:bool = [False, False, False, False, True]
shop_fuel:int
shop_goods:int
shop_equipment:str = []
shop_equipment_prices:int = []
# ennek segítségéven csak akkor generálódik új készlet, ha utaztunk
shop_has_been_generated:bool = False
# egy eladáskor az eladott áruk száma
goods_sold:int
# egy eladáskor a kapott kredit száma
credits_gained:float
# a status() metódusban ennek segítségéven íratjuk ki pontosan egyszer, utazás után az eladás adatait
goods_have_just_been_sold:bool = False
# százalékban, a landoláskor való felrobbanás esélye
chance_of_explosion:int=30
# a nyerés esélye százalékban, majd a utilize_equipment() metódus ad neki értéket
chance_of_winning:int
# maradt napok száma, utazásonként csökken 1-el
days_left:int = random.randrange(12, 16)
# hanyadik bolygó lesz a "The End"
the_end_xth_planet:int = random.randrange(10, 21)
# ennek segítségével nem fedezhetünk fel több bolygót, ha már felfedeztük az utolsót
the_end_has_been_generated:bool = False


def status():
    global goods_have_just_been_sold
    utilize_equipment()
    clear_screen()
    print(">>>>>------------------------------------------ S T A T U S ------------------------------------------<<<<<")
    if(chance_of_explosion != 0): print(f"change of explosion on landing:  {chance_of_explosion}%")
    print(f"fuel:  {fuel}/{max_fuel}")
    #print(f"location: {map[location]}")
    #print(f"map: {map}")
    #print(f"tech map:  {tech_map}")
    print(f"gps:  {gps()}")
    print(f"available telescopes:  {available_telescopes()}")
    #print(f"avarage tech level:  {tech_map_avarage()}")
    print("-----------------------------------------------------------------------------------------------------------")
    print(f"credits:  ${round(credits, 3)}", end="")
    if(goods_have_just_been_sold):
        print(f"      \033[32m{goods_sold} goods sold for ${credits_gained}\033[0m", end="")
        goods_have_just_been_sold = False
    print()

    print(f"goods:  {goods}/{max_goods}")

    if(equipment):
        print("equipment:   ", end="")
        print_equipment()
    print("-----------------------------------------------------------------------------------------------------------")
    print(f"days left: {days_left_colorized()}")
    print(f"chances of winning: {chance_of_winning}%")
    print("-----------------------------------------------------------------------------------------------------------")
    print("possible inputs:  travel, buy, telescope, fight")
    if(cheats): print("cheat:  /fuel, /credits, /planet, /explosion chance, /cheats")
    print("-----------------------------------------------------------------------------------------------------------")

def travel():
    global location
    global fuel
    global chance_of_explosion
    global shop_has_been_generated
    global days_left
    if(map[location] == "The End"):
        print("\n---you can't leave this planet---\n")
        print("Press Enter to continue.")
        input()
        return 0
    
    destination:str = str(input("where do you want to travel?: "))
    if(destination == ""):
        return 0
    elif(destination == "___"):
        print("\n---you cant land here---\n")
        print("Press Enter to continue.")
        input()
    elif(destination == map[location]):
        print("\n---you are already on this planet---\n")
        print("Press Enter to continue.")
        input()

    elif(destination in map):
        # az üzemanyaghasználat a helyünk és a célünk különbségének abszolútértéke
        fuelconsumption:int = abs(location-map.index(destination))
        if(fuelconsumption > fuel):
            print(f"\n---you dont have enough fuel---\nfuel needed: {fuelconsumption}   you have: {fuel}\n")
            print("Press Enter to continue.")
            input()
        else:
            if(random.randrange(1, 101) <= chance_of_explosion):
                clear_screen()
                print("\nGAME OVER: You failed the landing, your ship exploded.\n")
                print("Press Enter to exit...")
                input()
                exit()
            else:
                # utazunk, vagyis a helyt átállítjuk a célpontra
                location = map.index(destination)
                fuel -= fuelconsumption
                if(chance_of_explosion != 0): chance_of_explosion -= 1
                days_left -= 1
                # sikeres utazásnál automatikusan eladjuk az árut
                sell_goods()
                # utazás után a boltot újra lehet generálni, mert egy új bolygón vagyunk/a már meglátogatott bolygó készlete frissült az idő teltével
                shop_has_been_generated = False
    else:
        print("\n---destination does not exist---\n")
        print("Press Enter to continue.")
        input()

def buy():
    global credits
    global shop_fuel
    global shop_goods
    global fuel
    global goods
    global equipment
    global shop_equipment
    global shop_equipment_prices
    if(map[location] == "The End"):
        print("\n---there is no shop on this planet---\n")
        print("Press Enter to continue.")
        input()
        return 0
    if(shop_has_been_generated == False):
        generate_shop()
    print("shop items:\n")
    print(f"{shop_fuel} fuel   $1 per piece")
    print(f"{shop_goods} goods   $1 per piece\n")
    print_shop_equipment()
    to_buy:str=str(input("\nwhat do you want to buy?: "))
    # semmi vásárlása
    if(to_buy == "nothing" or to_buy == ""):
        ...
    
    # üzemanyag vásárlás
    elif(to_buy == "fuel"):
        while True:
            user_input = input("how much fuel do you want to buy?: ")
            if(user_input == ""):
                # annyi üzemanyagot veszünk amennyit tudunk, vagyis
                # min(amennyi pénzünk van, amennyi van a boltban, amennyi elfér)
                fuel_to_buy:int = min([int(credits), shop_fuel, max_fuel-fuel])
                credits -= round(fuel_to_buy, 3)
                shop_fuel -= fuel_to_buy
                fuel += fuel_to_buy
                return 0
            try:
                user_number = int(user_input)
                break
            except ValueError:
                print("\n---not a whole number---\n")
                print("Press Enter to continue.")
                input()
                return 0
        fuel_to_buy:int = user_number
        # ennek a felépítésnek az előnye: hogy ha a 3 közül bármelyik teljesül akkor az else ág nem fut le, és a 3 közül több is teljesülhet
        if((fuel_to_buy > credits) or (fuel_to_buy > shop_fuel) or (fuel + fuel_to_buy > max_fuel)):
            if(fuel_to_buy > credits):
                print("\n---you don't have enough credits---\n")
            if(fuel_to_buy > shop_fuel):
                print("\n---the shop doesn't have that much fuel---\n")
            if(fuel + fuel_to_buy > max_fuel):
                print("\n---your fuel tank is too small for that---\n")
            print("Press Enter to continue.")
            input()
        else:
            credits -= round(fuel_to_buy, 3)
            shop_fuel -= fuel_to_buy
            fuel += fuel_to_buy
    
    # áru vásárlás
    elif(to_buy == "goods"):
        while True:
            user_input = input("how many goods do you want to buy?: ")
            if(user_input == ""):
                # annyi árut veszünk amennyit tudunk, vagyis
                # min(amennyi pénzünk van, amennyi van a boltban, amennyi elfér)
                goods_to_buy:int = min([int(credits), shop_goods, max_goods-goods])
                credits -= round(goods_to_buy, 3)
                shop_goods -= goods_to_buy
                goods += goods_to_buy
                return 0            
            try:
                user_number = int(user_input)
                break
            except ValueError:
                print("\n---not a whole number---\n")
                print("Press Enter to continue.")
                input()
                return 0
        goods_to_buy:int = user_number
        if((goods_to_buy > credits) or (goods_to_buy > shop_goods) or (goods + goods_to_buy > max_goods)):
            if(goods_to_buy > credits):
                print("\n---you don't have enough credits---\n")
            if(goods_to_buy > shop_goods):
                print("\n---the shop doesn't have that many goods---\n")
            if(goods + goods_to_buy > max_goods):
                print("\n---you can't store that many goods---\n")
            print("Press Enter to continue.")
            input()
        else:
            credits -= round(goods_to_buy, 3)
            shop_goods -= goods_to_buy
            goods += goods_to_buy
    
    # felszerelés vásárlás
    elif(to_buy in shop_equipment):
        # A vagy B vagy C
        if(
            (shop_equipment_prices[shop_equipment.index(to_buy)] > credits) or
            ((to_buy != "container") and (to_buy != "translation device") and (to_buy in equipment)) or
            (
                ((to_buy == "medium tank") and ("large tank" in equipment)) or
                ((to_buy == "small tank") and ("medium tank" in equipment)) or
                ((to_buy == "small tank") and ("large tank" in equipment))
            )
        ):
            # A: HA nincs rá elég pénzünk AKKOR nem vehetjük meg
            if(shop_equipment_prices[shop_equipment.index(to_buy)] > credits):
                print("\n---you don't have enough credits---\n")
            # B: csak konténerből és tolmácsgépből lehet többet venni, vagyis  HA a venni kívánt tárgy nem konténer ÉS nem tolmácsgép ÉS már vettünk belőle, AKKOR nem vehetünk
            if((to_buy != "container") and (to_buy != "translation device") and (to_buy in equipment)):
                print("\n---you already have this equipment---\n")
            # C: HA a venni kívánt tanknál van már egy nagyobb tankunk, AKKOR nem vehetjük meg
            if(
                ((to_buy == "medium tank") and ("large tank" in equipment)) or
                ((to_buy == "small tank") and ("medium tank" in equipment)) or
                ((to_buy == "small tank") and ("large tank" in equipment))
            ):
                print("\n---you already have a bigger tank---\n")
            print("Press Enter to continue.")
            input()
        else:
            # sikeres felszerelés vásárlás
            equipment.append(to_buy)
            credits -= round(shop_equipment_prices[shop_equipment.index(to_buy)], 3)
            del shop_equipment_prices[shop_equipment.index(to_buy)]
            del shop_equipment[shop_equipment.index(to_buy)]
    else:
        print("\n---no such item---\n")
        print("Press Enter to continue.")
        input()

def telescope():
    global credits
    if(the_end_has_been_generated == True):
        print("\n---you have already discovered the final planet---\n")
        print("Press Enter to continue.")
        input()

    elif(telescope_map[location] == True):
        inputtext:str = str(input("do you want to use the telescope for $5? (yes/no): "))
        if(inputtext == "yes" or inputtext == ""):
            credits -= 5
            add_new_planet()
        elif(inputtext == "no"):
            ...
        else:
            print("\n---must be a yes or no answer---\n")
            print("Press Enter to continue.")
            input()
    else:
        print("\n---this planet doesn't have a telescope---\n")
        print("Press Enter to continue.")
        input()

def fight():
    if(map[location] == "The End"):
        if(random.randrange(1, 101) <= chance_of_winning):
            clear_screen()
            print("\nGAME WON: You beat the Ender Dragon.\n")
            print("Press Enter to exit...")
            input()
            exit()
        else:
            clear_screen()
            print("\nGAME OVER: You died, fighting the Ender Dragon.\n")
            print("Press Enter to exit...")
            input()
            exit()
    else:
        print("\n---there is no enemy to fight here---\n")
        print("Press Enter to continue.")
        input()



# a jelenlegi bolygó boltjának készletét legenerálja, a technikaifejlettségétől függően
def generate_shop():
    global shop_fuel
    global shop_goods
    global shop_equipment
    global shop_equipment_prices
    global shop_has_been_generated

    # üzemanyag random generálása 1 és 5 között a technikaifejlettségtől függően
    # ennek köszönhetően, óvatosan kell olyan alacsony technikaifejlettségű bolygóra utazni, ami más bolygóktól messze van, mert ottragadhatunk
    x:float = 15 / 5
    min:int = math.ceil(tech_map[location] / x) - 1
    max:int = math.ceil(tech_map[location] / x) + 4
    temp:int = random.randrange(min, max + 1)
    if(temp < 1): temp = 1
    if(5 < temp): temp = 5
    shop_fuel = temp

    # árú random generálása 0 és 40 között (1 és 41 között, utána kivonunk egyet), a technikaifejlettségtől függően
    x = 15 / 41
    min = math.ceil(tech_map[location] / x) - 5
    max = math.ceil(tech_map[location] / x) + 5
    temp:int = random.randrange(min, max + 1)
    if(temp < 1): temp = 1
    # a felső limit opcionális, ettől még 1 és 41 között lesz a randomgenerálás közepe (tech_map[location] / x), de ha 41 fölé esik akkor nem vágódik le
    #if(41 < temp): temp = 41
    temp -= 1
    shop_goods = temp

    # a felszerelések random generálása a technikaifejlettségtől függően
    shop_equipment = []
    shop_equipment_prices = []
    # ha a technikaifejlettség 6, akkor 108% eséllyel lesz dokkoló egység, ha 5 akkor 90%, ha 4 akkor 72%, ha 3 akkor 54% stb...
    if(random.randrange(1, 101) <= (tech_map[location] * 18)):
        shop_equipment.append("docking unit")
        shop_equipment_prices.append(10)
    # ha a technikaifejlettség 15, akkor 60% eséllyel lesz tolmácsgép, ha 14 akkor 56%, ha 13 akkor 52% stb...
    if(random.randrange(1, 101) <= (tech_map[location] * 4)):
        shop_equipment.append("translation device")
        shop_equipment_prices.append(5)
    # ha a technikaifejlettség 15, akkor 30% eséllyel lesz konténer, ha 14 akkor 28%, ha 13 akkor 26% stb...
    if(random.randrange(1, 101) <= (tech_map[location] * 2)):
        shop_equipment.append("container")
        shop_equipment_prices.append(3)

    if(random.randrange(1, 101) <= (tech_map[location] * 4)):
        shop_equipment.append("armor")
        shop_equipment_prices.append(random.randrange(15, 26))
    if(random.randrange(1, 101) <= (tech_map[location] * 3)):
        shop_equipment.append("plasma cannon")
        shop_equipment_prices.append(random.randrange(30, 51))
    if(random.randrange(1, 101) <= (tech_map[location] * 2)):
        shop_equipment.append("advanced missile launcher")
        shop_equipment_prices.append(random.randrange(45, 76))
    if(random.randrange(1, 101) <= (tech_map[location] * 1)):
        shop_equipment.append("rechargable alien energy shield")
        shop_equipment_prices.append(random.randrange(60, 101))

    if(random.randrange(1, 101) <= (tech_map[location] * 3)):
        shop_equipment.append("small tank")
        shop_equipment_prices.append(3)
    if(random.randrange(1, 101) <= (tech_map[location] * 2)):
        shop_equipment.append("medium tank")
        shop_equipment_prices.append(8)
    if(random.randrange(1, 101) <= (tech_map[location] * 1)):
        shop_equipment.append("large tank")
        shop_equipment_prices.append(16)   

    shop_has_been_generated = True

# generál egy új bolygót, hozzá technikaifejlettségi szintet, teleszkópot, és hozzáadja a térképhez
def add_new_planet():
    global map
    global tech_map
    global the_end_has_been_generated

    # a "The End" mindig az x-edik bolygó lesz
    if(len(map) == (the_end_xth_planet - 1)):
        map.append("The End")
        tech_map.append(16)
        telescope_map.append(False)
        the_end_has_been_generated = True

    # űrt generálunk 40% eséllyel, ha a térkép utolsó 3 eleme között van bolygó
    # ennek köszönhetően, ha generálódik 2 vagy 3 űr egymás után, akkor fejlesztenünk kell az üzemanyagtartályt, hogy át tudjuk utazni ezeket
    elif(random.randrange(1,101) <= 40 and (map[-1] != "___" or map[-2] != "___" or map[-3] != "___")):
        map.append("___")
        tech_map.append(0)
        telescope_map.append(False)

    # új bolygó generálása
    else:
        # a bolygó nevének random generálása
        VOWELS:str = ['a', 'e', 'i', 'o', 'u']
        CONSONANTS:str = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z']
        planet_name:str = map[0]
        # ellenőrízzük hogy ne forduljon elő már a "map"-ban, erre kicsi az esély, de elengedhetetlen a játék korrekt működéséhez
        while(planet_name in map):
            planet_name:str = ""
            # 3 és 6 karakter között, nagybetűvel kezdődik és 80% eséllyel mássalhangzóval, utána felváltva jönnek magánhangzók és mássalhangzók
            for i in range(random.randrange(3, 7)):
                if(len(planet_name) == 0):
                    if(random.randrange(1, 101) <= 80):
                        planet_name += random.choice(CONSONANTS).upper()
                    else:
                        planet_name += random.choice(VOWELS).upper()
                else:
                    if(planet_name[-1].lower() in VOWELS):
                        planet_name += random.choice(CONSONANTS)
                    else:
                        planet_name += random.choice(VOWELS)
        map.append(planet_name)

        # generáljuk az új bolygó technikaifejlettségét az átlagos technikaifejlettséghez relatívan random
        # így ahogy generálunk több és több bolygót, egyre magasabb lesz a technikaifejlettségük álltalában
        min:int = tech_map_avarage() - 6
        max:int = tech_map_avarage() + 10
        temp:int = random.randrange(min, max + 1)
        # nem  while(temp < 1 or 15 < temp)
        # ez a módszer jobb, mivel a nagyobb szám generálásának esélye nagyobb lesz, még akkor is ha a max 15 felé esik
        # tehát ha "tech_map_avarage()" = 14, akkor nagyobb eséllyel generál 15-öt,  mint 13-at, 12-őt, 11-et, 10-et stb...
        if(temp < 1): temp = 1
        if(15 < temp): temp = 15
        tech_map.append(temp)

        # ha a technikaifejlettség 15, akkor 50% eséllyel lesz teleszkóp, ha 14 akkor 46%, ha 13 akkor 43%, ha 12 akkor 40%, stb...
        if(random.randrange(1, 101) <= (temp * 3.34)):
            telescope_map.append(True)
        else: telescope_map.append(False)

# a felszereléseink hatásait végrehajtja,  kivéve a tolmácsgépét, az a sell_goods() metódusban látható
def utilize_equipment():
    global chance_of_explosion
    global max_goods
    global chance_of_winning
    global max_fuel

    # a dokkoló egység 0-ra állítja a robbanás esélyét
    if("docking unit" in equipment): chance_of_explosion = 0
    # ahány konténerünk van, annyiszor 4-el növekszik a szállítható áru
    if("container" in equipment):
        max_goods = 5 + (4 * equipment.count("container"))

    # 4 féle harci felszerelés van, mindegyik különböző százalékértékkel növeli a sikeres harc esélyét
    chance_of_winning = 0
    if("armor" in equipment): chance_of_winning += 10
    if("plasma cannon" in equipment): chance_of_winning += 20
    if("advanced missile launcher" in equipment): chance_of_winning += 30
    if("rechargable alien energy shield" in equipment): chance_of_winning += 40

    # 3 féle üzemanyagtartály van, ezeknek az az előnye, hogy nagyobb távolságot tudunk utazni, és jobban elkerülhetjük hogy egy bolygón ragadjunk
    if("small tank" in equipment and max_fuel < 3): max_fuel = 3
    if("medium tank" in equipment and max_fuel < 4): max_fuel = 4
    if("large tank" in equipment and max_fuel < 6): max_fuel = 6

# visszatér egy olyan térképpel ami mutatja hol vagyunk jelenleg, és technikaifejlettség alapján színkódol
def gps():
    #   0    1-3  4-6    7-9  10-12 13-15    The End
    # black  red yellow white green cyan     magenta
    string:str = ""
    temp:str
    for i in range(len(map)):
        temp = map[i]
        if(tech_map[i] == 0): temp = f"\033[30m{temp}\033[0m"
        if(1 <= tech_map[i] and tech_map[i] <= 3): temp = f"\033[31m{temp}\033[0m"
        if(4 <= tech_map[i] and tech_map[i] <= 6): temp = f"\033[33m{temp}\033[0m"
        if(7 <= tech_map[i] and tech_map[i] <= 9): temp = f"\033[37m{temp}\033[0m"
        if(10 <= tech_map[i] and tech_map[i] <= 12): temp = f"\033[32m{temp}\033[0m"
        if(13 <= tech_map[i] and tech_map[i] <= 15): temp = f"\033[36m{temp}\033[0m"
        if(map[i] == "The End"): temp = f"\033[35m{temp}\033[0m"
        if(location == i): temp = f"({temp})"
        string += temp + " "
    return string

# visszatér színkódolva azoknak a bolygóknak a nevével, ahol van teleszkóp
def available_telescopes():
    string:str = ""
    temp:str
    for i in range(len(map)):
        temp = map[i]
        if(telescope_map[i] == True):
            if(1 <= tech_map[i] and tech_map[i] <= 3): temp = f"\033[31m{temp}\033[0m"
            if(4 <= tech_map[i] and tech_map[i] <= 6): temp = f"\033[33m{temp}\033[0m"
            if(7 <= tech_map[i] and tech_map[i] <= 9): temp = f"\033[37m{temp}\033[0m"
            if(10 <= tech_map[i] and tech_map[i] <= 12): temp = f"\033[32m{temp}\033[0m"
            if(13 <= tech_map[i] and tech_map[i] <= 15): temp = f"\033[36m{temp}\033[0m"
            string += temp + " "
    return string

def sell_goods():
    global goods_have_just_been_sold
    global goods
    global credits
    global goods_sold
    global credits_gained
    if(map[location] == "The End"):
        ...
    elif(0 < goods):
        goods_sold = goods
        # minnél több tolmácsgépünk van, annál több a profit árueladáskor
        # a profit mennyisége eltérő mint a feladatleírásban, hogy gyorsabb legyen a játék, de a képlet ugyanaz
        # [-10; +50]%  árrés és egy tolmácsgép +15%-al  növeli
        #credits_gained = round(goods_sold * random.randrange(90 + (15 * equipment.count("translation device")), 151 + (15 * equipment.count("translation device"))) * 0.01, 3)
        # [-10; +100]% árrés és egy tolmácsgép +100%-al növeli
        credits_gained = round(goods_sold * random.randrange(90 + (100 * equipment.count("translation device")), 201 + (100 * equipment.count("translation device"))) * 0.01, 3)
        goods -= goods_sold
        credits += credits_gained
        goods_have_just_been_sold = True

def set_chance_of_explosion():
    global chance_of_explosion
    user_input = input("set chance of explosion to: ")
    if(user_input == ""):
        chance_of_explosion = 0
    else:
        # a try except szerkezet szükséges, hogy szöveg bemenetnél ne legyen hiba, és ne záródjon be a program
        try:
            user_number = int(user_input)
            if(user_number < 0 or 100 < user_number):
                print("\n---chance of explosion must be from 0 to 100---\n")
                print("Press Enter to continue.")
                input()
            else:
                chance_of_explosion = user_number
        except:
            print("\n---not a whole number---\n")
            print("Press Enter to continue.")
            input()

def set_fuel():
    global fuel
    global max_fuel
    user_input = input("set fuel to ")
    if(user_input == ""):
        fuel = 500
        max_fuel = 500
    else:
        try:
            user_number = int(user_input)
            if(user_number < 0):
                print("\n---fuel must be above 0---\n")
                print("Press Enter to continue.")
                input()
            else:
                fuel = user_number
                max_fuel = user_number
        except:
            print("\n---not a whole number---\n")
            print("Press Enter to continue.")
            input()

def set_credits():
    global credits
    user_input = input("set credits to ")
    if(user_input == ""):
        credits = 1000
    else:
        try:
            user_number = int(user_input)
            if(user_number < 0):
                print("\n---credits must be above 0---\n")
                print("Press Enter to continue.")
                input()
            else:
                credits = user_number
        except:
            print("\n---not a whole number---\n")
            print("Press Enter to continue.")
            input()

# kiírja a felszereléseinket, a "legjobbakat" magentában, és minden 4. elemenként rak sortörést és behúzást
def print_equipment():
    for i in range(len(equipment)):
        if(equipment[i] == "advanced missile launcher" or
           equipment[i] == "rechargable alien energy shield" or
           equipment[i] == "large tank"):
            print(f"\033[35m{equipment[i]}\033[0m   ", end="")
        else:
            print(f"{equipment[i]}   ", end="")
        # AKKOR rakunk sortörést és behúzást, HA [4 vagy többszöröse] db elemnél járunk ÉS ennél öszzesen több elem van(vagyis nem az az utolsó elem)
        # ezzel azt kerüljük el, hogy egy üres sor legyen, amikor pontosan [4 vagy többszöröse] db elem van
        if((i+1) in [4, 8, 12, 16, 20, 24, 28, 32] and (i+1) < len(equipment)): print(f"\n             ", end="")
    print()

# kiírja a bolt felszereléseit, a "legjobbakat" magentában
def print_shop_equipment():
    for i in range(len(shop_equipment)):
        if(shop_equipment[i] == "advanced missile launcher" or
           shop_equipment[i] == "rechargable alien energy shield" or
           shop_equipment[i] == "large tank"):
            print(f"\033[35m{shop_equipment[i]}\033[0m   ${shop_equipment_prices[i]}")
        else:
            print(f"{shop_equipment[i]}   ${shop_equipment_prices[i]}")

# visszatér a maradt napok számával, színkódolva
def days_left_colorized():
    if(days_left <= 4): return f"\033[31m{days_left}\033[0m"
    elif(days_left <= 8): return f"\033[33m{days_left}\033[0m"
    else: return days_left

# kiszámolja a technikaifejlettség átlagát, a 0 vagyis űr mezőket nem beleértve, és felfelé kerekíti
def tech_map_avarage():
    filtered_list:int=[]
    for i in range(len(tech_map)):
        if(tech_map[i] != 0): filtered_list.append(tech_map[i])
    return math.ceil(sum(filtered_list) / len(filtered_list))

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

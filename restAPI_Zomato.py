import requests

def city(): # dibuat menjadi fungsi karena akan dipakai 2x agar lebih efisien
    global entityId, citySuggName # dibuat menjadi global karena diperlukan di proses selanjutnya

    cityName, entityId = input("Masukkan nama kota : "), int()
    while not entityId: # entityId dijadikan determinan loop, dimana ia kemudian akan di ubah di proses selanjutnya apabila kota inputan user terdaftar
        reqLoc = requests.get(host + f"locations?query={cityName}", headers = headers).json()
        if reqLoc["location_suggestions"] == []:
            cityName = input("Nama kota yang Anda masukkan tidak terdaftar. Silahkan ulangi memberi masukkan : ")
        else:
            entityId = reqLoc["location_suggestions"][0]["entity_id"] # mengubah entityId sehingga kondisi while loop tidak terpenuhi lagi (exit loop)
            citySuggName = reqLoc["location_suggestions"][0]["title"]

def queryCount(query): # dibuat menjadi fungsi karena akan dipakai 2x agar lebih efisien
    global qC

    qC = input(f"Masukkan jumlah {query} yang akan ditampilkan : ")
    while qC or not qC:
        try:
            qC = int(qC) # input user harus bisa dijadikan int (hanya digit bulat)
            break
        except:
            qC = input(f"Anda salah memberi masukkan. Masukkan kembali jumlah {query} yang Anda ingin tampilkan : ")

print('''\n                                  # # # # # # # 
                                #               #
                               #                 #
                              #                   #
                              #  T O M A T O E S  #
                              #                   #
                               #                 #
                                #               #
                                 #             #
                                  #           #
                                    # # # # # ''') 
print("\n                                  W E L C O M E ")

ops = input("Silahkan pilih opsi di bawah ini: \n 1. Mencari Resto \n 2. Menu Harian \n Masukkan : ")
while (ops != "1") and (ops != "2"): # memaksa user memasukkan input 1 atau 2 saja
    ops = input("Anda salah memberi masukkan. Silahkan ulangi dengan memasukkan angka 1 untuk opsi 'Mencari Resto' atau angka 2 untuk opsi 'Menu Harian' \n Masukkan : ")

host, headers = "https://developers.zomato.com/api/v2.1/", {"user-key" : "3ec56806c64b2bf086316bf2cf94ff51"}
if ops == "1": # jika user pilih kondisi 1
    city() # untuk mendapatkan entityId, citySuggName
    print(f"'{citySuggName}' dipilih.")

    queryCount("restoran") # untuk mendapatkan qC

    sort = input("Apakah Anda ingin mengurutkan hasil berdasarkan rating tertinggi? \n Y / T \n Masukkan : ").upper()
    while (sort != "Y") and (sort != "T"): # memaksa user untuk hanya menginput Y atau T
        sort = input("Anda salah memberi masukkan. Ulangi kembali masukkan dengen mengetik Y untuk 'Ya' atau T untuk 'Tidak' \n Masukkan : ")

    sortDec = "" if sort == "T" else "&sort=rating&order=desc" # jika user pilih Y maka sort dan order dimasukkan, vice versa
    req = requests.get(host + f"search?entity_id={entityId}&entity_type=city" + sortDec, headers = headers).json()
    
    if len(req["restaurants"]) != 0:
        if len(req["restaurants"]) < qC:
            print(f"Maaf, namun sistem hanya mampu menampilkan {len(req['restaurants'])} restoran. Berikut daftarnya : \n")
        else:
            print("Berikut daftar restoran tersedia : \n")
        
        try: # try dan except digunakan untuk memenuhi asumsi bila qC (jumlah inputan user) melebihi jumlah yang tersedia hasil dari API
            for resto in range(qC):
                currentResto = req["restaurants"][resto]["restaurant"]
                print(f'''Nama restoran : {currentResto["name"]}
Tipe restoran : {", ".join(currentResto["establishment"])}
Tipe makanan dan minuman : {currentResto["cuisines"]}
Alamat : {currentResto["location"]["address"]}
No. Telepon : {currentResto["phone_numbers"].replace(" ", "")}
Rating : {currentResto["user_rating"]["aggregate_rating"]}
Review : {currentResto["all_reviews_count"]:,}\n''')
        except: # menghindari error dengan tidak melakukan apa - apa
            pass
    else:
        print("Maaf, sistem tidak menemukan daftar restoran di kota ini.")

else:
    city()
    print(f"'{citySuggName}' dipilih.")

    req = requests.get(host + f"search?entity_id={entityId}&entity_type=city", headers = headers).json()
    restoName, det = input("Masukkan nama restoran : ").lower(), 1
    while det: # det adalah variabel determinan untuk menjaga keberlangsungan while loop. det di define 1 pada awalnya untuk memulai loop
        for resto in req["restaurants"]:
            if restoName in resto["restaurant"]["name"].lower(): # jika nama restoran ada, maka det diubah menjadi 0 (False)
                restoId, det = resto["restaurant"]["R"]["res_id"], 0
                break # keluar loop for
        if det: # jika det masih sama dengan 1, maka memaksa user menginput kembali nama kotanya     
            restoName = input(f"Restoran yang Anda cari tidak terdaftar di {citySuggName}. Silahkan masukkan nama restoran yang lain : ")
        else: # jika det = 0 maka keluar while loop
            break
    
    reqDailyMenu = requests.get(host + f"dailymenu?res_id={restoId}", headers = headers)
    if reqDailyMenu.status_code == 200: # status code 200 tidak menjamin ada daily menu. maka dari itu, disisipkan kondisi lagi di dalamnya
        menuCount = reqDailyMenu.json()["daily_menus"][0]["daily_menu"]["dishes"]

        if menuCount != []: # jika len(menuCount) > 0
            queryCount("menu")
            if len(menuCount) < qC:
                print(f"Maaf, namun sistem hanya mampu menampilkan {len(menuCount)} menu harian. Berikut daftarnya : \n")
            else:
                print("Berikut daftar menu harian tersedia : \n")
            
            try:
                for x in range(qC):
                    print("{}".format(',\n'.join([menuCount[x]['dish']['name']])))
            except:
                pass
        else: # jika len(menuCount) == 0
            print("Maaf, sistem tidak menemukan daftar menu harian di restoran ini.")
    elif (reqDailyMenu.status_code == 400): # tidak ditemukan daftar menu di API
        print("Maaf, sistem tidak menemukan daftar menu harian di restoran ini.")
    else: # jika status code diluar 200 atau 400, misal 502 Bad Gateway, maka diasumsikan terjadi kesalahan jaringan
        print("Terjadi kesalahan pada jaringan. Silahkan ulangi kembali dalam beberapa waktu atau hubungi penyedia layanan.")

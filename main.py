import time
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
import names
import random
import string
import requests
import instaloader
from pyvis.network import Network
import progressbar



# The account you want to check
accounts = ["ericzemmour_", "universitegrenoblealpes"] #gauloisesansfiltre_", "julien.rochedy", "generationz.off", "action_francaise"


def construire_graph(cibles):
    conn = sqlite3.connect("ScrapFile.bd")
    cur = conn.cursor()
    g = nx.Graph()
    #cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    #tables = [entrees[0] for entrees in cur.fetchall()]

    tables = [cible + "_followers" for cible in cibles]
    print(tables)

    pseudos = [cur.execute(f"SELECT pseudo, '{table[:-10]}' FROM '{table}'").fetchall() for table in tables]
    pseudos = [(pseudo[0], pseudo[1]) for liste in pseudos for pseudo in liste]

    conn.close()

    g.add_edges_from(pseudos)


    return g, tables, pseudos

def afficher_graph(cibles, intermediaire, g, tables, pseudos):

    tout_pseudos = len(pseudos)
    deja_delete = set()
    for cpt, table in enumerate(tables):
        a_delete = set()
        with progressbar.ProgressBar(max_value=tout_pseudos) as bar2:
            for cpt2, pseudo in enumerate(pseudos):
                bar2.update(cpt2)
                try:
                    if pseudo[0] not in deja_delete and len(nx.shortest_path(g, pseudo[0], table[:-10])) > intermediaire+2:
                        a_delete.add(pseudo[0])
                except:
                    a_delete.add(pseudo[0]) #pas de chemin

        tout_a_delete = len(a_delete)
        with progressbar.ProgressBar(max_value=tout_a_delete) as bar3:
            for cpt3, pseudo in enumerate(a_delete):
                bar3.update(cpt3)
                if pseudo + "_followers" not in tables and pseudo not in deja_delete:
                    g.remove_node(pseudo)
                    deja_delete.add(pseudo)

    color_map = []
    liste_nodes = []
    for node in g:
        liste_nodes.append(node)
        if node in cibles:
            color_map.append('red')
        else:
            color_map.append('blue')

    print(len(liste_nodes))
    print(liste_nodes)

    nx.draw(g, with_labels=True, node_color=color_map)
    plt.show()

    nx.draw(g, with_labels=True, node_color=color_map)
    plt.show()

    nx.draw_random(g, with_labels=True, node_color=color_map)
    plt.show()

    nx.draw_circular(g, with_labels=True, node_color=color_map)
    plt.show()

    nx.draw_spectral(g, with_labels=True, node_color=color_map)
    plt.show()

    nx.draw_spring(g, with_labels=True, node_color=color_map)
    plt.show()
    #net = Network()
    #net.from_nx(g)
    #net.show("exemple.html")

def get_and_save(account, profondeur):
    print("************************************************")
    print(f"creation de la table des followers de {account}")
    conn = sqlite3.connect('ScrapFile.bd')
    cur = conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS '{account}_followers'")
    cur.execute(
        f"CREATE TABLE IF NOT EXISTS '{account}_followers' (id INTEGER PRIMARY KEY, pseudo varchar(100) NOT NULL)")


    print(f"recuperation des followers de {account}")
    debut = time.time()
    temp = time.time()
    profile = instaloader.Profile.from_username(L.context, account)
    total = profile.followers
    followers = []
    i = 1
    for follower in profile.get_followers():
        followers.append(follower.username)
        if i%200 == 0:
            print(f"{i} comptes recuperés sur {total}")
            time.sleep(0.2)
        if i%1000 == 0:
            print(f"enregistrement des 1000 dernieres entrées en base")
            cur.executemany(f"INSERT INTO '{account}_followers' (pseudo) VALUES (?)", [(f,) for f in followers])
            conn.commit()
            followers = []
            print(f"1000 entrées en {time.time()-temp} secondes")

            print(f"10 secondes de pause")
            time.sleep(10)
            temp = time.time()
        if i%2500 == 0:
            print(f"45 secondes de pause")
            time.sleep(45)
        if i%5000 == 0:
            print(f"1 minute 45 secondes de pause")
            time.sleep(105)
        if i%7500 == 0:
            print(f"2 minutes de pause")
            time.sleep(120)
        if i % 25000 == 0:
            print(f"5 minutes de pause")
            time.sleep(300)
        i = i+1

    if len(followers) > 0:
        cur.executemany(f"INSERT INTO '{account}_followers' (pseudo) VALUES (?)", [(f,) for f in followers])
        conn.commit()
        conn.close()

    print(f"{account} : {total} comptes recupérés en {time.time()-debut} secondes")
    print("************************************************\n\n")



    if profondeur > 1:
        for acc in followers:
            print("5 minutes de pause")
            time.sleep(300)
            get_and_save(acc, profondeur-1)


accounts = ["ericzemmour_", "aix_studentlife"] #gauloisesansfiltre_", "julien.rochedy", "generationz.off", "action_francaise", "univlyon1"
if __name__ == "__main__":
    L = instaloader.Instaloader()
    L.login("clementcaffin", "vodka2B")
    skip = ["action_francaise", "gauloisesansfiltre_", "ericzemmour_", "julien.rochedy", "generationz.off", "bde.sciencespolyon", "aix_studentlife"]

    for account in accounts:
        if account not in skip:
            get_and_save(account, 1)
            pass
        else:
            print(f"{account} skip")
            pass

    g, tables, pseudos = construire_graph(accounts)
    afficher_graph(accounts, 0, g, tables, pseudos)
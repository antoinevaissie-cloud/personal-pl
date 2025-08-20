from etl.bnp import load_bnp_csv
from etl.boursorama import load_boursorama_csv
from etl.revolut import load_revolut_csv

def test_bnp_loader_basic():
    content = (
        "Compte de chèques ****6388;Solde au 12/08/2025;3248 66;EUR;;;\n"
        ";;;;;;\n"
        "Date operation;Categorie operation;Sous Categorie;Libelle;Montant\n"
        "05-07-2025;Revenus;Virement;VIREMENT;1 234,50\n"
        "06-07-2025;Paiements;Carte;CARTE CAFE;-12,34\n"
    ).encode("cp1252")
    rows = load_bnp_csv(content)
    assert len(rows) == 2
    assert rows[0]["amount"] == 1234.50
    assert rows[1]["amount"] == -12.34

def test_boursorama_loader_basic():
    content = (
        "dateOp;dateVal;label;category;categoryParent;supplierFound;amount;comment;accountNum;accountLabel;accountbalance\n"
        "2025-07-01;2025-07-01;CARTE 30/06/25 SUPERMARCHE;Courses;Maison;;-45.20;;000123;Compte joint;2500.00\n"
    ).encode("cp1252")
    rows = load_boursorama_csv(content)
    assert len(rows) == 1
    assert rows[0]["amount"] == -45.20
    assert rows[0]["currency"] == "EUR"

def test_revolut_loader_basic():
    content = (
        "Type,Product,Started Date,Completed Date,Description,Amount,Fee,Currency,State,Balance\n"
        "CARD_PAYMENT,Current,2025-07-01 10:00:00,2025-07-01 10:01:00,COFFEE,-3.50,0.00,GBP,COMPLETED,1000.00\n"
    ).encode("utf-8")
    rows = load_revolut_csv(content)
    assert len(rows) == 1
    assert rows[0]["amount"] == -3.50
    assert rows[0]["currency"] == "GBP"

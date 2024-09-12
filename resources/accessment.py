import io

import pandas
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required
from flask_smorest import Blueprint, abort
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import AccessmentModel
from schemas import AccessmentSchema

blp = Blueprint("Accessments", __name__, description="Operations on accessments")


def GetAccessment():
    driver = webdriver.Chrome()

    driver.get(f"https://www.cnyes.com/twstock/board/ratediff.aspx")
    soup = BeautifulSoup(driver.page_source, "lxml")
    soup.encoding = "utf-8"
    table = soup.select_one("#ctl00_ContentPlaceHolder1_divRate")
    dfs = pandas.read_html(io.StringIO(str(table.prettify())), flavor="bs4")[0]
    # dfs["成交"] = dfs["成交"].astype(float)
    # dfs = dfs[(dfs["成交"] > "40") & (dfs["代號"] != "代號")]
    # dfs["累月  營收  連增減  年數"] = (
    #     dfs["累月  營收  連增減  年數"].str.replace("連", "").str.replace("增", "")
    # )
    # # dfs = dfs.drop(dfs[(dfs.代號 == "代號")].index)
    # dfs = dfs.iloc[:, [0, 4, 8, 18]]
    return dfs


@blp.route("/accessment")
class Item(MethodView):
    @blp.response(200, AccessmentSchema)
    def get(self):
        dfs = GetAccessment()
        return dfs

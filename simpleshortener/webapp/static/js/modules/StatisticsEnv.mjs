/*jshint esversion: 6 */
"use strict";

import Layout from "./Layout.mjs";
import {TargetUrl} from "./Url.mjs";

export default class StatisticsEnv {
    constructor() {
        this._urlList = [];

        this.layout = new Layout(this._urlList);

        this._loadUrlList();
    }

    _loadUrlList() {
        fetch('./api/v2/url_list').then((res) => {
            if (res.headers.get("content-type") && res.headers.get("content-type").includes("application/json"))
                return res.json();
            throw new TypeError("Oops, we haven't got JSON!");
        }).then((data) => {
            while (this._urlList.length) this._urlList.pop();
            data.forEach((i) => this._urlList.push(new TargetUrl(i[0], i[1])));

            this.layout.drawer.open = true;
        });
    }
}
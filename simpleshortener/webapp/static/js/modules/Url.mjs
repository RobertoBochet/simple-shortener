/*global Chart, componentHandler*/
/*jshint esversion: 6 */
"use strict";

import {colorGenerator} from "./Color.js";

let _colorGenerator = null;

export class Url {
	constructor(url) {
		this.url = url;
		this.isSelected = false;
		this.metrics = null;
	}

	get_time_metrics() {
		return this.metrics["date"];
	}

	get_ua_metrics() {
		return this.metrics["user-agent"];
	}
}

export class ShortUrl extends Url {
	constructor(shortUrl) {
		super(shortUrl);

		this.color = _colorGenerator.next().value;
	}
}

export class TargetUrl extends Url {
	constructor(targetUrl, shortUrl) {
		super(targetUrl);

		this.shortUrl = [];

		_colorGenerator = colorGenerator();
		for (let s of shortUrl) {
			this.shortUrl.push(new ShortUrl(s));
		}
	}

	loadStatistics(callback = null) {
		fetch('./api/v2/metrics', {
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'
			},
			method: "POST",
			body: JSON.stringify({url: this.url})
		}).then((res) => {
			if (res.headers.get("content-type") && res.headers.get("content-type").includes("application/json")) {
				return res.json();
			}
			throw new TypeError("Oops, we haven't got JSON!");
		}).then((data) => {

			this.metrics = data;

			//Updates time chart
			this.metrics["period"]["start"] = new Date(Date.parse(this.metrics["period"]["start"]));
			this.metrics["period"]["end"] = new Date(Date.parse(this.metrics["period"]["end"]));


			this.shortUrl.forEach((i) => {
				this.metrics["short"].forEach((j) => {
					if (i.url === j.url) {
						i.metrics = j;
					}
				});
			});

			if (callback !== null)
				callback(this);
		});
	}
}
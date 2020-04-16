/*jshint esversion: 6 */
"use strict";

import {TargetUrl} from "./Url.mjs";
import {COLOR, colorGenerator} from "./Color.js";


export default class MetricsProcessor {
	static processUA(targetUrl, ...shortUrl) {
		let cg = colorGenerator();
		let ua = [];

		let url = targetUrl ? [targetUrl, ...shortUrl] : shortUrl;

		url.forEach((u) => {
			Object.keys(u.get_ua_metrics()).forEach((k) => {
				if (!ua.includes(k)) ua.push(k)
			});
		});

		let data = {
			datasets: [],
			labels: ua
		};

		let bg = ua.map(u => COLOR.user_agent[u] || cg.next().value);

		url.forEach((u) => {
			let v = {
				data: [],
				backgroundColor: bg,
				borderColor: "#000",
				borderWidth: u instanceof TargetUrl ? 1 : 0
			};

			ua.forEach((k) => {
				v.data.push(k in u.get_ua_metrics() ? u.get_ua_metrics()[k] : 0);
			});

			data.datasets.push(v);
		});

		return data;
	}

	static processTime(period, targetUrl, ...shortUrl) {
		let cg = colorGenerator();
		let data = {
			labels: [],
			datasets: []
		};

		let days = [];

		for (let day = period["start"];
		     day <= period["end"];
		     day = new Date(day.getTime() + 60 * 60 * 24 * 1000)) {
			days.push(day);
		}

		data.labels = days.map(x => x.strftime("%Y-%m-%d"));
		days = days.map(x => x.strftime("%Y-%m-%d"));

		if (targetUrl) {
			let metrics = targetUrl.get_time_metrics();
			let dataset = {
				type: "line",
				label: "total",
				lineTension: 0,
				borderColor: COLOR.total,
				backgroundColor: "rgba(0,0,0,0)",
				data: []
			};
			days.forEach(d => {
				dataset.data.push(d in metrics ? metrics[d]["total"] : 0);
			});
			data.datasets.push(dataset);
		}

		shortUrl.forEach(u => {
			let metrics = u.get_time_metrics();
			let dataset = {
				stack: 'short',
				label: u.url,
				barPercentage: 0.3,
				backgroundColor: u.color,
				data: []
			};
			days.forEach(d => {
				dataset.data.push(d in metrics ? metrics[d]["total"] : 0);
			});
			data.datasets.push(dataset);
		});

		return data;
	}
}
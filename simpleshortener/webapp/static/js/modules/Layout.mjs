/*jshint esversion: 6 */
/*global mdc, Chart*/
"use strict";

import {TargetUrl} from "./Url.mjs";
import Vue from "https://cdn.jsdelivr.net/npm/vue@2.6.11/dist/vue.esm.browser.min.js";
import MetricsProcessor from "./MetricsProcessor.mjs";

export default class Layout {
	constructor(targetUrlList) {
		this._targetUrlList = targetUrlList;

		this.drawer = new mdc.drawer.MDCDrawer(document.querySelector('.mdc-drawer'));

		this.topAppBar = new mdc.topAppBar.MDCTopAppBar(document.querySelector('.mdc-top-app-bar'));
		this.topAppBar.setScrollTarget(document.querySelector('main'));
		this.topAppBar.listen('MDCTopAppBar:nav', () => {
			this.drawer.open = !this.drawer.open;
		});

		this.dataTable = new mdc.dataTable.MDCDataTable(document.querySelector('.mdc-data-table'));

		this.mainApp = new Vue({
			el: "#main",
			data: {
				isSelected: false,
				targetUrl: new TargetUrl("", [])
			},
			methods: {
				change: (e) => {
					if (!e.isSelected) this.mainApp.isSelected = false;
					this._updateCharts(this.mainApp.targetUrl);
				},
				changeMain: () => {
					[this.mainApp.targetUrl, ...this.mainApp.targetUrl.shortUrl].forEach(e => e.isSelected = this.mainApp.isSelected);
					this._updateCharts(this.mainApp.targetUrl);
				}
			}
		});

		this.targetUrlApp = new Vue({
			el: "#target-url-list",
			data: {
				targetUrl: this._targetUrlList
			},
			methods: {
				click: (url) => {
					this.drawer.open = false;
					url.loadStatistics(() => {
						this.mainApp.targetUrl = url;
						this.mainApp.isSelected = false;
						this.mainApp.targetUrl.shortUrl.forEach(e => e.isSelected = false);
						this.mainApp.targetUrl.isSelected = true;
						this._updateCharts(url);

						// Waits Vue update
						setTimeout(() => this.dataTable.layout(), 500);
					});
				}
			}
		});

		this._buildCharts();
	}

	_buildCharts() {
		this.charts = {
			time: new Chart(document.getElementById("chart-time").getContext("2d"), {
				type: "bar",
				options: {
					title: {
						display: true,
						text: "Visit vs days"
					},
					tooltips: {
						mode: 'index',
						intersect: false
					},
					responsive: true,
					scales: {
						xAxes: [{
							stacked: true,
						}],
						yAxes: [{
							stacked: true,
							beginAtZero: true,
							ticks: {
								precision:0
							}
						}]
					}
				}
			}),
			ua: new Chart(document.getElementById("chart-ua").getContext("2d"), {
				type: "doughnut",
				options: {
					title: {
						display: true,
						text: "User agents"
					}
				}
			})
		}
	}

	_updateCharts(url) {
		this._updateUAChart(url);
		this._updateTimeChart(url);
	}

	_updateUAChart(url) {
		this.charts.ua.data = MetricsProcessor.processUA(
			url.isSelected ? url : null,
			...url.shortUrl.filter(u => u.isSelected));
		this.charts.ua.update();
	}

	_updateTimeChart(url) {
		this.charts.time.data = MetricsProcessor.processTime(
			url.metrics["period"],
			url.isSelected ? url : null,
			...url.shortUrl.filter(u => u.isSelected));
		this.charts.time.update();
	}
}

function sleep(milliseconds) {
	let start = new Date().getTime();
	for (let i = 0; i < 1e7; i++) {
		if ((new Date().getTime() - start) > milliseconds) {
			break;
		}
	}
}

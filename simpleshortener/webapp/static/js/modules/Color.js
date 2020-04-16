/*jshint esversion: 6 */
"use strict";

export const COLOR = {
	total: "#444",
	user_agent: {
		"linux": "#ffc500",
		"windows": "#00a4ef",
		"android": "#3ddc84",
		"ios": "#aee1cd",
		"mac": "#6534ff",
		"other": "#6a6a6a"
	},
	random: ["#0000ff", "#ff00e0", "#ff8f00", "#0087ff"]
};

export function* colorGenerator() {
	yield* COLOR.random;
	while (true) yield "#" + ((1 << 24) * Math.random() | 0).toString(16);
}

export default COLOR;
import{A as u,B as s,h as a,C as f,D as l}from"./index.54e2b61a.js";const d=n=>u(s(n)),m=n=>u(n);function h(n,t){return n!==void 0&&n()||t}function g(n,t){if(n!==void 0){const e=n();if(e!=null)return e.slice()}return t}function p(n,t){return n!==void 0?t.concat(n()):t}function y(n,t,e,r,i,c){t.key=r+i;const o=a(n,t,e);return i===!0?f(o,c()):o}function S(n,t){const e=n.style;for(const r in t)e[r]=t[r]}function x(n){if(n==null)return;if(typeof n=="string")try{return document.querySelector(n)||void 0}catch{return}const t=l(n);if(t)return t.$el||t}function D(n,t){if(n==null||n.contains(t)===!0)return!0;for(let e=n.nextElementSibling;e!==null;e=e.nextElementSibling)if(e.contains(t))return!0;return!1}export{g as a,p as b,d as c,S as d,m as e,y as f,x as g,h,D as i};

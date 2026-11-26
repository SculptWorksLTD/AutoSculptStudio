// AutoSculpt Studio - phone page. © 2026 Enrico Migliorati. All rights reserved.
// Only what makes the page installable on the home screen: every request goes to the network.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', () => {});

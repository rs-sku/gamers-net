import assert from 'node:assert/strict';
import test from 'node:test';
import { getAllPages, getAllPagesResponse } from '../frontend/js/api/pagination.js';
import { getAllUsers } from '../frontend/js/api/auth.js';
import { getAllGames, getUserGames } from '../frontend/js/api/games.js';
import { getFriendshipOverview, getFriends } from '../frontend/js/api/friends.js';

test('collects empty, exact and multiple pages without losing records', async () => {
    for (const size of [0, 100, 205]) {
        const records = Array.from({ length: size }, (_, id) => ({ id }));
        const calls = [];
        const result = await getAllPages(async ({ limit, offset }) => {
            calls.push(offset);
            assert.equal(limit, 100);
            return records.slice(offset, offset + limit);
        });
        assert.deepEqual(result, records);
        assert.deepEqual(calls, size === 0 ? [0] : size === 100 ? [0, 100] : [0, 100, 200]);
    }
});

test('preserves HTTP errors from later pages rather than returning partial data', async () => {
    const failure = new Response(JSON.stringify({ detail: 'Not authenticated' }), { status: 401 });
    const result = await getAllPagesResponse(async ({ offset }) => offset === 0
        ? Response.json(Array.from({ length: 100 }, (_, id) => ({ id })))
        : failure);
    assert.equal(result, failure);
    await assert.rejects(getAllPages(async () => ({ invalid: true })), /invalid list/);
    await assert.rejects(getAllPagesResponse(async () => { throw new Error('offline'); }), /offline/);
});

test('existing API consumers receive complete lists with their original shapes', async () => {
    const records = Array.from({ length: 205 }, (_, id) => ({ id: id + 1 }));
    const requests = [];
    const originalFetch = globalThis.fetch;
    globalThis.fetch = async (url, options) => {
        const parsed = new URL(url);
        requests.push(parsed);
        assert.equal(options.credentials, 'include');
        assert.equal(parsed.searchParams.get('limit'), '100');
        const offset = Number(parsed.searchParams.get('offset'));
        const page = records.slice(offset, offset + 100);
        return Response.json(parsed.pathname.endsWith('/friends') ? { friends: page } : page);
    };
    try {
        assert.deepEqual(await (await getAllUsers()).json(), records);
        assert.deepEqual(await getAllGames(), records);
        assert.deepEqual(await getUserGames(7), records);
        assert.deepEqual(await getFriends('user'), { friends: records });
        assert.deepEqual(await getFriendshipOverview('user'), {
            users: records, friends: records, incoming: records, outgoing: records
        });
        assert.equal(requests.length, 24);
        for (const url of requests) {
            if (url.pathname === '/api/v1/games') assert.equal(url.searchParams.get('user_id'), '7');
            if (url.pathname.endsWith('/friends')) assert.equal(url.searchParams.get('name'), 'user');
            if (url.pathname.endsWith('-friend-requests')) {
                assert.equal(url.searchParams.get('status'), 'pending');
            }
        }
    } finally {
        globalThis.fetch = originalFetch;
    }
});

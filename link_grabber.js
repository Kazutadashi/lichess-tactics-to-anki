var chess_links = document.querySelectorAll('.mini-board');
var chess_links_list = [];
for (let i = 0; i < chess_links.length; i++) {
    chess_links_list.push('https://lichess.org/api/puzzle/' + chess_links[i].getAttribute('href').slice(-5));
}
console.log(chess_links_list)

document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    const roundNumberElement = document.getElementById('round-number');
    const timeLeftElement = document.getElementById('time-left');
    const blockListElement = document.getElementById('block-list');
    const bidForm = document.getElementById('bid-form');
    const submittedBidsList = document.getElementById('submitted-bids-list');
    const endRoundButton = document.getElementById('end-round');

    let roundNumber = 0;
    let timeLeft = 60;
    let timer;

    socket.on('round_data', function(data) {
        roundNumber = data[0].round;
        roundNumberElement.textContent = roundNumber;
        blockListElement.innerHTML = '';
        data.forEach(block => {
            const listItem = document.createElement('li');
            listItem.textContent = `Blok ${block.block}: ${block.current_bid} zł`;
            if (block.highest_bidder === '{{ user }}') {
                listItem.textContent += ' (Jesteś zwycięzcą)';
            }
            blockListElement.appendChild(listItem);
        });
        startTimer();
    });

    function startTimer() {
        clearInterval(timer);
        timeLeft = 60;
        timer = setInterval(() => {
            timeLeft -= 1;
            timeLeftElement.textContent = timeLeft;
            if (timeLeft <= 0) {
                clearInterval(timer);
                socket.emit('end_round');
            }
        }, 1000);
    }

    bidForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const block = document.getElementById('block').value;
        const bidAmount = document.getElementById('bid-amount').value;

        socket.emit('submit_bid', { block: block, bid_amount: bidAmount });
        const listItem = document.createElement('li');
        listItem.textContent = `Blok ${block}: ${bidAmount} zł`;
        submittedBidsList.appendChild(listItem);
    });

    endRoundButton.addEventListener('click', function() {
        socket.emit('end_round');
    });

    socket.emit('join', { user: '{{ user }}' });
});
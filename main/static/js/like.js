// like.js - Handles like functionality
export function initLikes() {
    document.querySelectorAll('.like-btn').forEach(button => {
        button.addEventListener('click', handleLikeClick);
    });
}

function handleLikeClick(event) {
    event.preventDefault();
    const button = event.currentTarget;
    const postId = button.dataset.postId;
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    
    fetch(`/like/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const likeCount = button.querySelector('.like-count');
            likeCount.textContent = data.likes_count;
            
            if (data.liked) {
                button.classList.add('liked');
                button.setAttribute('title', 'Beğeniden kaldır');
            } else {
                button.classList.remove('liked');
                button.setAttribute('title', 'Beğen');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
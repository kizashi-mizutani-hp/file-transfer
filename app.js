async function uploadFile() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];

    if (!file) {
        alert('ファイルを選択してください。');
        return;
    }

    // ファイルサイズの制限を100KBに設定
    const maxSize = 1 * 1024 / 10; // 100KB = 102,400 bytes
    //const maxSize = 1 * 1024 * 1024; // 1MB = 1,048,576 bytes
    console.log(file.size);
    if (file.size > maxSize) {
        alert('ファイルサイズが100KBを超えています。別のファイルを選択してください。');
        return;
    }

    // API GatewayのエンドポイントURL（実際のURLに置き換えてください）
    //const apiUrl = 'https://kpi3wmteek.execute-api.ap-northeast-1.amazonaws.com';
    const apiUrl = 'https://kpi3wmteek.execute-api.ap-northeast-1.amazonaws.com/test/generate-url';

    try {
        // サーバーから事前署名付きURLを取得
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'file_name': file.name,
                'content_type': file.type || 'application/octet-stream'
            }),
            // CORS対応のための設定
            mode: 'cors',
        });
        const data = await response.json();
        console.log('URL取得に成功:', data);

        const uploadUrl = data.upload_url;
        const downloadUrl = data.download_url;

        // ファイルを事前署名付きURLにアップロード
        const uploadResponse = await fetch(uploadUrl, {
            method: 'PUT',
            headers: {
                'Content-Type': file.type || 'application/octet-stream'
            },
            mode: 'cors',
            body: file
        });

        if (uploadResponse.ok) {
            const messageElement = document.getElementById('message');
            messageElement.innerHTML = `
                ファイルがアップロードされました。<br>
                ダウンロードURL: <a href="${downloadUrl}" target="_blank">${downloadUrl}</a>
            `;
        } else {
            alert('ファイルのアップロードに失敗しました。');
        }
    } catch (error) {
        console.error(error);
        alert('エラーが発生しました。');
    }
}

from PIL import Image, ImageChops

def trim_image_with_margin(
    image_path: str,
    output_path: str, 
    margin: int=10,
    initial_bottom_crop: int = 250
):
    """

    画像の下部を最初に切り取り、その後余白をトリミングして保存する関数。

    Args:
        image_path (str): 入力画像のファイルパス。
        margin (int): コンテンツの周りに残す余白のピクセル数。
        output_path (str): トリミング後の画像を保存するファイルパス。
        initial_bottom_crop (int): 最初に画像下部から切り取るピクセル数。
    
    """
    try:
        # 画像を開く
        with Image.open(image_path) as img:
            # 最初に画像の下部を指定ピクセル分だけ切り取る
            if initial_bottom_crop > 0:
                width, height = img.size
                if initial_bottom_crop >= height:
                    print(f"警告: 下部の切り取りピクセル数({initial_bottom_crop}px)が画像の高さ({height}px)以上です。この処理はスキップします。")
                else:
                    # (left, top, right, bottom) の形式で切り取り範囲を指定
                    crop_box = (0, 0, width, height - initial_bottom_crop)
                    img = img.crop(crop_box)
                    print(f"画像の下部から {initial_bottom_crop} ピクセルを最初に切り取りました。")
            # --- ▲ここまでが追加した機能▲ ---

            # 画像の背景色を取得（左上隅の色を背景色と仮定）
            bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
            
            # 背景色と異なる部分を計算
            diff = ImageChops.difference(img, bg)
            
            # アルファチャンネルがある場合も考慮
            if diff.mode == 'RGBA':
                diff_rgb = diff.convert('RGB')
                bbox = diff_rgb.getbbox()
            else:
                bbox = diff.getbbox()

            # コンテンツが見つからない場合（画像が単色の場合など）
            if not bbox:
                print("コンテンツが見つからなかったため、余白のトリミングをスキップしました。")
                img.save(output_path)
                return

            # バウンディングボックス (left, top, right, bottom)
            left, top, right, bottom = bbox

            # マージンを適用した新しいバウンディングボックスを計算
            new_left = max(0, left - margin)
            new_top = max(0, top - margin)
            new_right = min(img.width, right + margin)
            new_bottom = min(img.height, bottom + margin)
            
            crop_box = (new_left, new_top, new_right, new_bottom)

            # 計算したボックスで画像をトリミング
            cropped_img = img.crop(crop_box)
            
            # 結果を保存
            cropped_img.save(output_path)
            print(f"トリミングした画像を '{output_path}' に保存しました。")

    except FileNotFoundError:
        print(f"エラー: ファイル '{image_path}' が見つかりません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
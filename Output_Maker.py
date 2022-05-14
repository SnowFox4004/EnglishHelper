def Make_html(contents, filename, GLOBAL_PATH):
    head = r'''
    <!DOCTYPE html>
   <head>
		<meta charset="UTF-8">
		<style>
			blockquote{
				display:block;
				background:#fff;
				padding:15px 20px 15px 20px;
				margin: 0 0 20px;

				/*字体*/
				font-family:Goergia,serif;
				font-size:16px;
				line-height:1.2;
				color:#666;
				text-align:justify;
				
				/*边框*/
				border-left:15px solid #429296;
				border-right:2px solid #429296;

				/*盒子阴影*/
				-moz-box-shadow:2px 2px 15px #ccc;
				-webkit-box-shadow:2px 2px 15px #ccc;
				box-shadow:2px 2px 15px #ccc;

			}
			blockquote:before{
				content:"\201C";

				/*字体*/
				font-family:Georgia,serif;
				font-size:60px;
				font-weight:bold;
				color:#999;

				/*位置*/
				position:absolute;
				left:10px;
				top:auto;

			}
			blockquote:after{
				content:"\"
			}
			h1 {
				color: cyan;
				text-align:center;
				margin-left:-100px
			}   
			small {
				color : black;
				text-align : right
			}
			.orange {
			    color : orange;
			}
			
		</style>
   </head>
   <body>
		<h1>H T M L 词 库</h1>
		<blockquote>
			<<INDEXFORREPLACE>>
		</blockquote>
		
		<small> <small><small><small>Made by FrostFoxII</small></small></small></small>
   </body>
    '''
    replaceit = ''
    for i in contents:
        add = i.replace(' ', ' ').replace('\n', '<br>')
        add = add.replace('<ASPACE>', ' ')
        replaceit += add

    head = head.replace('<<INDEXFORREPLACE>>', replaceit)
    print(replaceit)
    open(f'{GLOBAL_PATH}/htmls/{filename}.html', 'w+', encoding='utf-8').write(head)


def Make_ff2(contents, filename, GLOBAL_PATH):
    open(f'{GLOBAL_PATH}/ff2/{filename}.ff2', 'w+', encoding='utf-8').write(str(contents))


if __name__ == '__main__':
    Make_html(['a,b,c,d,e,f,g\n', '1,2,3, b      4,5,6,7\n'], 'test1', '.')

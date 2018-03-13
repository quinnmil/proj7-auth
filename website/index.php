<html>
    <head>
        <title>Project 6 - restful api</title>
    </head>

    <body>

        <h1>/listAll</h1>
        <ul>
            <?php
            $json = file_get_contents('http://laptop-service/listAll');

            $obj = json_decode($json);
            $times = $obj->result;
            if ($times == []){
                echo "Database is empty"; 
            } else{
                foreach($times as $k) {
                    $open = $k->open;
                    $close = $k->close;
                    $distance = $k->km;
                    echo "<li>Open:$open</li><li>Close:$close</li><li>Distance:$distance</li>";

                }
            }
            ?>
        </ul>
        <h1>/ListOpenOnly</h1>
        <ul>
            <?php
            $json = file_get_contents('http://laptop-service/listOpenOnly');

            $obj = json_decode($json);
            $times = $obj->result;
            if ($times == []){
                echo "Database is empty"; 
            } else{
                foreach($times as $k) {
                    $open = $k->open;
                    $distance = $k->km;
                    echo "<li>Open: $open</li>";
                    echo "<li>Open: $distance</li>";

                }
            }
            ?>
        </ul>
        <h1>/ListCloseOnly</h1>
        <ul>
            <?php
            // $top = $_GET['top'];
            // echo "<li>$top</li>";
            // $url = "http://laptop-service/listCloseOnly/top/" . $top;
            // echo "<li>$url</li>";

            // $url = 'http://laptop-service/listClosedOnly/?top=' . urlencode($top);
            
            $json = file_get_contents('http://laptop-service/listCloseOnly');

            $obj = json_decode($json);
            $times = $obj->result;
            if ($times == []){
                echo "Database is empty"; 
            } else{
                foreach($times as $k) {
                    $close = $k->close;
                    $distance = $k->km;
                    // not sure if I should print distances. 
                    echo "<li>Close: $close</li>";
                    echo "<li>Distance: $distance</li>";

                }

            }
            ?>
        </ul>
        <h1>/ListAll Top 3</h1>
        <ul>
            <?php
            $json = file_get_contents('http://laptop-service/listAll?top=3');

            $obj = json_decode($json);
            $times = $obj->result;
            if ($times == []){
                echo "Database is empty"; 
            } else{
                foreach($times as $k) {
                    $open = $k->open;
                    $close = $k->close;
                    $distance = $k->km;
                    echo "<li>Open:$open</li><li>Close:$close</li><li>Distance:$distance</li>";

                }
            }
            ?>
        </ul>
        <h1>/ListCloseOnly Top 2</h1>
        <ul>
            <?php
            // $top = $_GET['top'];
            // echo "<li>$top</li>";
            // $url = "http://laptop-service/listCloseOnly/top/" . $top;
            // echo "<li>$url</li>";

            // $url = 'http://laptop-service/listClosedOnly/?top=' . urlencode($top);
            
            $json = file_get_contents('http://laptop-service/listCloseOnly?top=2');

            $obj = json_decode($json);
            $times = $obj->result;
            if ($times == []){
                echo "Database is empty"; 
            } else{
                foreach($times as $k) {
                    $close = $k->close;
                    $distance = $k->km;
                    // not sure if I should print distances. 
                    echo "<li>Close: $close</li><li>Distance: $distance</li>";

                }

            }
            ?>
        </ul>
         <h1>/listAllCsv</h1>
        <ul>
        <?php
        $entry = file_get_contents('http://laptop-service/listAll/csv');
        echo nl2br($entry);
                   

            ?>
        </ul>

        <h1>/listOpenOnlyCsv</h1>
        <ul>
            <?php
            $data = file_get_contents('http://laptop-service/listOpenOnly/csv');
            echo nl2br($data);
            ?>
        </ul>

           <h1>/listClosedOnlyCsv</h1>
        <ul>
            <?php
            $data = file_get_contents('http://laptop-service/listCloseOnly/csv');
            echo nl2br($data);
            ?>
        </ul>
    </body>
    </html>
  




       
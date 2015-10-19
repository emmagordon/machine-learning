(defproject clj-ml7 "0.1.0-SNAPSHOT"
  :description "FIXME: write description"
  :url "http://example.com/FIXME"
  :dependencies [[org.clojure/clojure "1.5.1"]
                 [org.clojure/math.numeric-tower "0.0.4"]
                 [cc.artifice/clj-ml "0.4.0"]
                 [incanter "1.5.4"]
                    [org.clojure/data.csv "0.1.2"]]
  :jvm-opts ["-Djsse.enableSNIExtension=false"]
  
  :repl-options {
             ;; If nREPL takes too long to load it may timeout,
             ;; increase this to wait longer before timing out.
             ;; Defaults to 30000 (30 seconds)
             :timeout 200000
             }
  
  :main clj-ml7.core  
  
  
  
  )

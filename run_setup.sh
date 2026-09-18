# # ruby path
# export PATH="/opt/homebrew/opt/ruby/bin:$PATH"
# # jekyll path
# # sudo gem install --user-install bundler jekyll
# export PATH=${PATH}:/Users/colmar/.gem/ruby/3.1.0/bin

# # sudo gem install racc
# # bundle install
# # bundle exec jekyll build

# bundle exec jekyll -v
# bundle exec jekyll server

# #bundle add webrick 




export PATH="/opt/homebrew/opt/ruby@3.1/bin:/opt/homebrew/lib/ruby/gems/3.1.0/bin:$PATH"
export SDKROOT="$(xcrun --show-sdk-path)"
export CPLUS_INCLUDE_PATH="$SDKROOT/usr/include/c++/v1"
export C_INCLUDE_PATH="$SDKROOT/usr/include"
export CPATH="$SDKROOT/usr/include"
export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig"

bundle exec jekyll server 